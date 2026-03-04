---
publishDate: 2024-08-21T00:00:00Z
title: 'TDD 实现 Spring（DI容器）'
excerpt: '本文介绍了如何使用 TDD 的方式实现一个简单的 Spring DI 容器，包含注入点的支持、组件的构造、依赖的选择以及生命周期控制。'
category: 'TDD'
tags:
  - TDD
metadata:
  canonical: https://nobug.world/blogs/25729/
---

# [](#TDD-实现-DI-容器简介 "TDD 实现 DI 容器简介")TDD 实现 DI 容器简介

TDD 的难点首先在于理解需求，并将需求分解为功能点。

以 Jakarta EE 中的 Jakarta Dependency Injection 为主要功能参考，并对其适当简化，以完成我们的目标

实现 DI 时参考 Jakarta Dependency Injection，其中的功能主要分为三部分：

*   注入点的支持、组件的构造
    
*   依赖的选择
    
*   生命周期控制（多例和单例）
    

使用@Inject标注的方法或字段，被称为注入点

> 常见的注入方式有：构造函数注入、字段注入、方法注入
> 
> > 在 JSR330 中还包含两个可选的注入方式：静态方法的注入、静态字段的注入
> 
> 如果不考虑易于测试的情况下，更倾向于构造函数注入

容器会找到被注入点，并找到所需的实例，再注入进来，来完成注入。

典型的错误是出现循环依赖的情况，JSR330 中规定了使用 Provider。

# [](#使用-Guice-演示-DI-容器如何使用，包含哪些功能 "使用 Guice 演示 DI 容器如何使用，包含哪些功能")使用 Guice 演示 DI 容器如何使用，包含哪些功能

> 做解释的原因：在开发之前都需要澄清需求、理解需求
> 
> 实际开发中，呈现需求的方式有：user story、PRD（Product Requirement Document，产品需求文档）等方式
> 
> 在TDD中，也是不能直接上来就写测试的，也是需要先理解需求和上下文

Jakarta Dependency Injection 中没有规定而又常用的部分有：容器如何配置、容器层级结构以及生命周期回调。

*   如何形成配置文件
*   容器层级结构便于生命周期管理
*   生命周期回调

> 这些功能步包含在 JRS330 中，更多的是在企业级环境中需要，所以不在当前项目的考虑范围中。

# [](#功能分解 "功能分解")功能分解

对于组件构造部分，分解的任务大致如下：

*   无需构造的组件：即直接将实例注册进容器
    
*   如果注册的组件不可实例化，则抛出异常
    
    *   抽象类
    *   接口
*   构造函数注入
    
    *   无依赖的组件应该通过默认构造函数生成组件实例
    *   有依赖的组件，通过 Inject 标注的构造函数生成组件实例
    *   如果所依赖的组件也存在依赖，那么需要对所依赖的组件也完成依赖注入
    *   如果组件有多于一个 Inject 标注的构造函数，则抛出异常
    *   如果组件需要的依赖不存在，则抛出异常
    *   如果组件间存在循环依赖，则抛出异常
*   字段注入
    
    *   通过 Inject 标注将字段声明为依赖组件
    *   如果组件需要的依赖不存在，则抛出异常
    *   如果字段为 final 则抛出异常
    *   如果组件间存在循环依赖，则抛出异常
*   方法注入
    
    *   通过 Inject 标注的方法，其参数为依赖组件
        
    *   通过 Inject 标注的无参数方法，会被调用
        
    *   按照子类中的规则，覆盖父类中的 Inject 方法
        
    *   如果组件需要的依赖不存在，则抛出异常
        
    *   如果方法定义类型参数，则抛出异常
        
    *   如果组件间存在循环依赖，则抛出异常
        

对于依赖选择部分，我分解的任务列表如下：

*   对 Provider 类型的依赖
    
    *   注入构造函数中可以声明对于 Provider 的依赖
    *   注入字段中可以声明对于 Provider 的依赖
    *   注入方法中可声明对于 Provider 的依赖
*   自定义 Qualifier 的依赖
    
    *   注册组件时，可额外指定 Qualifier
        
    *   注册组件时，可从类对象上提取 Qualifier
        
    *   寻找依赖时，需同时满足类型与自定义 Qualifier 标注
        
    *   支持默认 Qualifier——Named
        

对于生命周期管理部分，我分解的任务列表如下：

*   Singleton 生命周期
    
    *   注册组件时，可额外指定是否为 Singleton
    *   注册组件时，可从类对象上提取 Singleton 标注
    *   对于包含 Singleton 标注的组件，在容器范围内提供唯一实例
    *   容器组件默认不是 Single 生命周期
*   自定义 Scope 标注
    
    *   可向容器注册自定义 Scope 标注的回调

# [](#新建项目 "新建项目")新建项目

新建一个gradle项目，build.gradle.kts配置文件如下：

```kotlin
1   plugins {
2       `java-library`
3       "jacoco"
4   }
5   repositories {
6       mavenCentral()
7   }
8   dependencies {
9       implementation("jakarta.inject:jakarta.inject-api:2.0.1")
10      testImplementation("org.junit.jupiter:junit-jupiter-api:5.8.2")
11      testImplementation("org.junit.jupiter:junit-jupiter-params:5.8.2")
12      testRuntimeOnly("org.junit.jupiter:junit-jupiter-engine:5.8.2")
13      testRuntimeOnly("org.junit.vintage:junit-vintage-engine:5.8.2")
14      testRuntimeOnly("org.junit.platform:junit-platform-runner:1.8.2")
15      testImplementation("org.mockito:mockito-core:4.3.1")
16      testImplementation("jakarta.inject:jakarta.inject-tck:2.0.1")
17  }
18  tasks.withType<Test>() {
19      useJUnitPlatform()
20  }
21  java {
22      sourceCompatibility = JavaVersion.VERSION_17
23      targetCompatibility = JavaVersion.VERSION_17
24  }
```

# [](#开始红-绿-重构循环 "开始红-绿-重构循环")开始红-绿-重构循环

测试类：

```java
1   public class ContainerTest {
2   
3       // 组件构造相关的测试类
4       @Nested
5       public class ComponentConstruction{
6           
7       }
8       
9       // 依赖选择相关的测试类
10      @Nested
11      public class DependenciesSelection{
12          
13      }
14      
15      // 生命周期管理相关的测试类
16      @Nested
17      public class LifecycleManagement{
18          
19      }
20  }
```

先将要测试的内容使用@Nested注解隔离成不同的范围，这种结构可以帮助你更好地组织和编写测试。

> 在JUnit 5中，`@Nested`注解用于表示内部类，这些内部类可以作为特定测试的一部分。这种结构可以帮助你更好地组织和编写测试，特别是当你需要对一个类的不同方面或不同状态进行大量测试时。
> 
> 使用`@Nested`注解的内部类可以有它们自己的测试方法，`@BeforeEach`和`@AfterEach`方法，甚至它们自己的`@BeforeAll`和`@AfterAll`方法。这使得你可以在每个内部类级别上设置和清理测试环境，从而为每个测试提供独立的环境。
> 
> 如上代码中，`ComponentConstruction`类被标记为`@Nested`，这意味着它可以包含一组相关的测试，这些测试可以共享相同的初始化和清理代码。

将ComponentConstruction中的测试再细分为构造器注入、字段注入、方法注入等测试

```java
1   @Nested
2   public class ComponentConstruction{
3   
4       // TODO: instance
5       // TODO: abstract class
6       // TODO: interface
7   
8       @Nested
9       public class ConstructorInjection{
10          
11      }
12  
13      @Nested
14      public class FieldInjection{
15  
16      }
17  
18      @Nested
19      public class MethodInjection{
20  
21      }
22  
23  }
```

给ConstructorInjection增加一些todo

```java
1   @Nested
2   public class ConstructorInjection{
3       // TODO: No args constructor
4       // TODO: with dependencies
5       // TODO: A -> B -> C
6   }
```

# [](#TODO-instance "TODO: instance")TODO: instance

直接向容器中注册实例。

### [](#构造测试 "构造测试")构造测试

新建测试，并使编译通过：

```java
1   // TODO: instance
2   @Test
3   public void should_bind_type_to_a_specific_instance() {
4   
5       Context context = new Context();
6   
7   	// 创建一个实现了 Component 接口的匿名内部类实例
8       Component instance = new Component() {
9       };
10      context.bind(Component.class, instance);
11  
12      assertSame(instance, context.get(Component.class));
13  }
```

> 创建了一个匿名内部类（即 `new Component() {}`），它实现了 `Component` 接口。由于这是一个匿名内部类，所以它没有名字，但它的行为与任何其他实现了 `Component` 接口的类是一样的。

要使编译通过，需要创建Context和其中的bind、get方法：

```java
1   public class Context {
2   
3       public <ComponentType> void bind(Class<ComponentType> type, ComponentType instance) {
4   
5       }
6   
7       public <ComponentType> ComponentType get(Class<ComponentType> typeClass) {
8           return null;
9       }
10  }
```

编译通过，如果运行测试，那么这时会有异常：

```plaintext
1   org.opentest4j.AssertionFailedError: expected: <world.nobug.tdd.di.ContainerTest$ComponentConstruction$1@2dc9b0f5> but was: <null>
2   	at org.junit.jupiter.api.AssertionUtils.fail(AssertionUtils.java:55)
3   	at org.junit.jupiter.api.AssertSame.failNotSame(AssertSame.java:48)
4   	at org.junit.jupiter.api.AssertSame.assertSame(AssertSame.java:37)
5   	at org.junit.jupiter.api.AssertSame.assertSame(AssertSame.java:32)
6   	at org.junit.jupiter.api.Assertions.assertSame(Assertions.java:2851)
```

### [](#快速实现 "快速实现")快速实现

将bind的信息存入一个map中即可实现

```java
1   public class Context {
2   
3       private Map<Class<?>, Object> components = new HashMap<>();
4   
5       public <ComponentType> void bind(Class<ComponentType> type, ComponentType instance) {
6           components.put(type, instance);
7       }
8   
9       public <ComponentType> ComponentType get(Class<ComponentType> type) {
10          return (ComponentType) components.get(type);
11      }
12  }
```

接下来继续实现其他todo，一般我们先从happy path开始，这里先从构造器注入开始

# [](#TODO-No-args-constructor "TODO: No args constructor")TODO: No args constructor

向容器中注册一个类型，该类型有一个默认构造函数。

当需要从容器中获取get这个类型的实例时，容器应该调用这个默认构造函数以创建一个实例。

### [](#构造测试-1 "构造测试")构造测试

```java
1   // TODO: No args constructor
2   @Test
3   public void should_bind_type_to_a_class_with_default_constructor() {
4       Context context = new Context();
5   
6       context.bind(Component.class, ComponentWithDefaultConstructor.class);
7   
8       Component instance = context.get(Component.class);
9   
10      assertNotNull(instance);
11      assertInstanceOf(ComponentWithDefaultConstructor.class, instance);
12  }
```

Context新增bind方法

```java
1   public <ComponentType, ComponentImplementation extends ComponentType>
2   void bind(Class<ComponentType> type, Class<ComponentImplementation> implementation) {
3   
4   }
```

### [](#快速实现-1 "快速实现")快速实现

因为要支持两种bind方式，所以要快速实现并不容易。

当然如果在不计任何罪恶的情况下，也可以再新建一个Map保存这种bind形式的数据

```java
1   public class Context {
2   
3       private Map<Class<?>, Object> components = new HashMap<>();
4       private Map<Class<?>, Class<?>> componentImplementations = new HashMap<>();
5   
6       public <ComponentType> void bind(Class<ComponentType> type, ComponentType instance) {
7           components.put(type, instance);
8       }
9   
10      public <ComponentType> ComponentType get(Class<ComponentType> type) {
11          if (components.containsKey(type))
12              return (ComponentType) components.get(type);
13          Class<?> implementation = componentImplementations.get(type);
14          try {
15              // 获取到默认构造函数，并创建实例
16              return (ComponentType)implementation.getConstructor().newInstance();
17          } catch (Exception e) {
18              throw new RuntimeException(e);
19          }
20      }
21  
22      public <ComponentType, ComponentImplementation extends ComponentType>
23      void bind(Class<ComponentType> type, Class<ComponentImplementation> implementation) {
24          componentImplementations.put(type, implementation);
25      }
26  }
```

### [](#重构 "重构")重构

两个map并不是一个合理的实现方式，并且还有if else，这些都是坏味道。需要重构，并且前面的测试已经证明了功能的可用性。有了测试的保证就可以进行安全的重构。

如何重构：将这两个map中的value值类型合并为使用同一个interface，或者说使用同一种形式的API。

在JSR330中已经提供了一个Provider

```java
1   public interface Provider<T> {
2       T get();
3   }
```

> 其实这就是一个Factory

在注册时，将这两个注册的方法，分别的变成Provider

```java
1   private Map<Class<?>, Provider<?>> providers = new HashMap<>();
```

> Java8提供了与Provider接口类似的Supplier函数式接口，这里只是选用了JSR330的接口，功能是一样的

接下来就是进行逐步替换掉这两个Map

#### [](#替换components "替换components")替换components

先替换第一个bind方法：

```java
1   public <ComponentType> void bind(Class<ComponentType> type, ComponentType instance) {
2       components.put(type, instance);
3       providers.put(type, () -> instance);
4   }
```

对应的修改get方法，将用到components的地方替换为使用providers

```java
1   public <ComponentType> ComponentType get(Class<ComponentType> type) {
2       if (providers.containsKey(type))
3           return (ComponentType) providers.get(type).get();
4       Class<?> implementation = componentImplementations.get(type);
5       try {
6           return (ComponentType)implementation.getConstructor().newInstance();
7       } catch (Exception e) {
8           throw new RuntimeException(e);
9       }
10  }
```

修改代码后，运行测试

紧接着移除，bind方法中的components语句，就会发现components的map就不需要使用了，可以将这个map移除

```java
1   private Map<Class<?>, Class<?>> componentImplementations = new HashMap<>();
2   private Map<Class<?>, Provider<?>> providers = new HashMap<>();
3   
4   public <ComponentType> void bind(Class<ComponentType> type, ComponentType instance) {
5       providers.put(type, () -> instance);
6   }
```

#### [](#替换componentImplementations "替换componentImplementations")替换componentImplementations

同理，针对componentImplementations这个map做替换，替换完成后Context的现实如下：

```java
1   public class Context {
2   
3       private Map<Class<?>, Provider<?>> providers = new HashMap<>();
4   
5       public <ComponentType> void bind(Class<ComponentType> type, ComponentType instance) {
6           providers.put(type, () -> instance);
7       }
8   
9       public <ComponentType, ComponentImplementation extends ComponentType>
10      void bind(Class<ComponentType> type, Class<ComponentImplementation> implementation) {
11          providers.put(type, () -> {
12              try {
13                  return implementation.getConstructor().newInstance();
14              } catch (Exception e) {
15                  throw new RuntimeException(e);
16              }
17          });
18      }
19  
20      public <ComponentType> ComponentType get(Class<ComponentType> type) {
21          return (ComponentType) providers.get(type).get();
22      }
23  }
```

至此，就已经实现了一个基本的DI容器的结构，之后就是要围绕 DI 容器的基本结构，对其进行更多功能上的完善。

### [](#重构总结 "重构总结")重构总结

在重构的时候，我采用的是增加一个平行实现（Parallel Implementation）。用平行实现替换原有功能，然后再删除原有实现的做法。

# [](#简单重构 "简单重构")简单重构

在继续后面的功能之前，先梳理一下测试，进行一些简单的重构。

目前每一个测试中都需要构造一个新的Context，可以预见到后续的每一个测试也都需要构造Context。

重构测试，将构造新的Context的动作放到setup中，并移除掉后续方法中创建Context的语句。

```java
1   Context context;
2   
3   @BeforeEach
4   public void setUp(){
5       context = new Context();
6   }
```

重构测试，将Component接口，及其相关子类移动到ContainerTest的外部，方便阅读。

![Snipaste_2024-08-08_16-20-52](~/assets/images/spring-di/Snipaste_2024-08-08_16-20-52.png)

# [](#TODO-with-dependencies "TODO: with dependencies")TODO: with dependencies

构造被`@Inject`标注的构造函数的测试，并通过编译

## [](#构造测试-2 "构造测试")构造测试

```java
1   // TODO: with dependencies
2   @Test
3   public void should_bind_type_to_a_class_with_inject_constructor() {
4       Dependency dependency = new Dependency() {
5       };
6       context.bind(Component.class, ComponentWithInjectConstructor.class);
7       context.bind(Dependency.class, dependency);
8   
9       Component instance = context.get(Component.class);
10      assertNotNull(instance);
11      assertSame(dependency, ((ComponentWithInjectConstructor) instance).getDependency());
12  }
13  
14  interface Dependency{
15  }
16  
17  class ComponentWithInjectConstructor implements Component{
18      private Dependency dependency;
19  
20      @Inject
21      public ComponentWithInjectConstructor(Dependency dependency){
22          // 注意，一定要记得赋值
23          this.dependency = dependency;
24      }
25  
26      // 用于测试验证dependency是否被注入
27      public Dependency getDependency() {
28          return dependency;
29      }
30  }
```

## [](#简单重构-1 "简单重构")简单重构

简单重构，重命名范型名称，简短一点

ComponetType -> Type

\-> Implementation

## [](#快速实现-2 "快速实现")快速实现

### [](#第一步 "第一步")第一步

修改newInstance时的代码，创建时应该传入依赖的实例，但目前还是使用默认构造函数，所以还是依然会出错，但这只是第一步。

```java
1   public <Type, Implementation extends Type>
2   void bind(Class<Type> type, Class<Implementation> implementation) {
3       providers.put(type, () -> {
4           try {
5               Constructor<Implementation> injectConstructor = implementation.getConstructor();
6               // 根据构造函数的参数，获取依赖的实例
7               Object[] dependencies = Arrays.stream(injectConstructor.getParameters())
8                       .map(p -> get(p.getType()))
9                       .toArray(Object[]::new);
10              return injectConstructor.newInstance(dependencies);
11          } catch (Exception e) {
12              throw new RuntimeException(e);
13          }
14      });
15  }
```

### [](#第二步 "第二步")第二步

提取获取构造器的方法

```java
1   public <Type, Implementation extends Type>
2   void bind(Class<Type> type, Class<Implementation> implementation) {
3       providers.put(type, () -> {
4           try {
5               Constructor<Implementation> injectConstructor = getInjectConstructor(implementation);
6               // 根据构造函数的参数，获取依赖的实例
7               Object[] dependencies = Arrays.stream(injectConstructor.getParameters())
8                       .map(p -> get(p.getType()))
9                       .toArray(Object[]::new);
10              return injectConstructor.newInstance(dependencies);
11          } catch (Exception e) {
12              throw new RuntimeException(e);
13          }
14      });
15  }
```

获取带`@Inject`的构造器或默认构造器

```java
1   private static <Type> Constructor<Type> getInjectConstructor(
2           Class<Type> implementation) {
3       Stream<Constructor<?>> injectConstructors = Arrays.stream(implementation.getConstructors())
4               .filter(c -> c.isAnnotationPresent(Inject.class));
5       return (Constructor<Type>) injectConstructors.findFirst().orElseGet(() -> {
6           try {
7               return implementation.getConstructor();
8           } catch (NoSuchMethodException e) {
9               throw new RuntimeException(e);
10          }
11      });
12  }
```

# [](#TODO-A-B-C "TODO: A -> B -> C")TODO: A -> B -> C

有传递性的依赖

## [](#构造测试-3 "构造测试")构造测试

构造并运行测试，会发现测试直接通过，说明当前的生产代码已经满足了我们的功能需求，不需要修改生产代码。

```java
1   // TODO: A -> B -> C
2   @Test
3   public void should_bind_type_to_a_class_with_inject_transitive_dependencies() {
4       context.bind(Component.class, ComponentWithInjectConstructor.class);
5       context.bind(Dependency.class, DependencyWithInjectConstructor.class);
6       context.bind(String.class, "Hello World!");
7   
8       Component instance = context.get(Component.class);
9       assertNotNull(instance);
10  
11      Dependency dependency = context.get(Dependency.class);
12      assertNotNull(dependency);
13  
14      assertEquals("Hello World!", ((DependencyWithInjectConstructor) dependency).getDependency());
15  }
```

```java
1   class DependencyWithInjectConstructor implements Dependency{
2       // 直接使用字符串类型，不新建接口，简化开发
3       private String dependency;
4   
5       @Inject
6       public DependencyWithInjectConstructor(String dependency){
7           this.dependency = dependency;
8       }
9   
10      public String getDependency() {
11          return dependency;
12      }
13  }
```

# [](#何时处理sad-path "何时处理sad path")何时处理sad path

到目前为止，部分happy path已经完成，还剩下一些sad path，这样我们就有了一个选择，就是继续做happy path（去做FieldInjection、MethodInjection）还是做sad path

两种选择都可以，但是有些不一样的地方。

应该在经过一定时间的happy path的任务编写后，应该转到sad path，前面的happy path是为了尽快确定我们的代码结构，同时sad path也会需要我们调整代码结构，所以应该及时在开发了一段时间的happy path需求后引入一些sad path来促进代码结构的变化。

# [](#TODO：multi-inject-constructors "TODO：multi inject constructors")TODO：multi inject constructors

有多个构造函数被`@Inject`注解标记的情况，JSR330中规定只能有一个构造函数被`@Inject`标注

## [](#构造测试-4 "构造测试")构造测试

创建包含两个被`@Inject`注解标记的构造方法的类作为测试数据

```java
1   class ComponentWithMultiInjectConstructors implements Component{
2   
3       @Inject
4       public ComponentWithMultiInjectConstructors(String name, Double value){
5       }
6   
7       @Inject
8       public ComponentWithMultiInjectConstructors(String name){
9       }
10  }
```

测试代码：

```java
1   // TODO：multi inject constructors
2   @Test
3   public void should_throw_exception_if_multi_inject_constructors_provided() {
4       assertThrows(IllegalComponentException.class, () -> {
5           context.bind(Component.class, ComponentWithMultiInjectConstructors.class);
6       });
7   }
```

这里是在bind的时候校验是否异常，也可以在get的时候校验异常:

```java
1   assertThrows(IllegalComponentException.class, () -> {
2       context.get(Component.class);
3   });
```

**但是这里选择在bind是校验的原因是，可以及时短路，也会使后续的代码更加简单。**

创建IllegalComponentException异常类

```java
1   public class IllegalComponentException extends RuntimeException {
2   }
```

## [](#快速实现-3 "快速实现")快速实现

在bind方法中增加校验

```java
1   Constructor<?>[] injectConstructors =
2                   Arrays.stream(implementation.getConstructors()).filter(c -> c.isAnnotationPresent(Inject.class))
3                           .toArray(Constructor<?>[]::new);
4           if (injectConstructors.length > 1) throw new IllegalComponentException();
```

# [](#TODO-no-default-constructor-and-inject-constructor "TODO: no default constructor and inject constructor")TODO: no default constructor and inject constructor

没有默认构造函数且没有被`@Inject`注解标注的构造函数的情况

## [](#构造测试-5 "构造测试")构造测试

构造没有默认构造函数和被`@Inject`注解标注的构造函数的测试类

```java
1   class ComponentWithNoInjectConstructorNorDefaultConstructor implements Component {
2   
3       public ComponentWithNoInjectConstructorNorDefaultConstructor(String name) {
4       }
5   }
```

测试方法：

```java
1   // TODO: no default constructor and inject constructor
2   @Test
3   public void should_throw_exception_if_no_inject_constructor_nor_default_constructor_provided() {
4       assertThrows(IllegalComponentException.class, () -> {
5           context.bind(Component.class, ComponentWithNoInjectConstructorNorDefaultConstructor.class);
6       });
7   }
```

## [](#快速实现-4 "快速实现")快速实现

在bind方法中增加校验

```java
1   if (injectConstructors.length < 1 &&
2                   Arrays.stream(implementation.getConstructors()).noneMatch(c -> c.getParameterCount() == 0))
3               throw new IllegalComponentException();
```

# [](#重构-1 "重构")重构

## [](#调整-bind-中对默认构造函数的校验逻辑 "调整 bind 中对默认构造函数的校验逻辑")调整 bind 中对默认构造函数的校验逻辑

通过观察发现在 bind 中找校验构造函数是否合规的方法，和后面的 getInjectConstructor 的方法的逻辑是有部分重叠的，都需要获取到构造函数的列表。

在 getInjectConstructor 中会校验默认构造函数的情况，只需要在 getInjectConstructor 方法中抛出 IllegalComponentException 异常，并将 providers.put 方法中的 getInjectConstructor 方法提前到 put 方法之前，就可以移除掉 bind 方法中对默认构造函数的校验。

> 将 providers.put 方法中的 getInjectConstructor 方法提前到 put 方法之前，是因为 put 时只是创建一个匿名内部类，并不会执行 getInjectConstructor 方法，getInjectConstructor 方法是在 get 时调用。

![](~/assets/images/spring-di/Snipaste_2024-08-09_15-41-19.png)

![](~/assets/images/spring-di/Snipaste_2024-08-09_15-41-51.png)

## [](#调整-bind-中对多个被-Inject-标注的构造函数的校验逻辑 "调整 bind 中对多个被 Inject 标注的构造函数的校验逻辑")调整 bind 中对多个被 Inject 标注的构造函数的校验逻辑

同理，也可将校验是否有多个被 Inject 标注的构造函数的逻辑放到 getInjectConstructor 方法中

这样就可以将 bind 中的校验代码移除，改写后的 getInjectConstructor 方法如下：

```java
1   private static <Type> Constructor<Type> getInjectConstructor(
2           Class<Type> implementation) {
3       List<Constructor<?>> injectConstructors = Arrays.stream(implementation.getConstructors())
4               .filter(c -> c.isAnnotationPresent(Inject.class)).toList();
5       if (injectConstructors.size() > 1) throw new IllegalComponentException();
6   
7       return (Constructor<Type>) injectConstructors.stream().findFirst().orElseGet(() -> {
8           try {
9               return implementation.getConstructor();
10          } catch (NoSuchMethodException e) {
11              throw new IllegalComponentException();
12          }
13      });
14  }
```

# [](#TODO-dependencies-not-exist "TODO: dependencies not exist")TODO: dependencies not exist

组件中的依赖不存在的情况

## [](#构造测试-6 "构造测试")构造测试

```java
1   // TODO: dependencies not exist
2   @Test
3   public void should_throw_exception_if_dependency_not_found() {
4       context.bind(Component.class, ComponentWithInjectConstructor.class);
5   
6       assertThrows(DependencyNotFoundException.class, () -> {context.get(Component.class);});
7   }
```

复用了 ComponentWithInjectConstructor

```java
1   class ComponentWithInjectConstructor implements Component{
2       private Dependency dependency;
3   
4       @Inject
5       public ComponentWithInjectConstructor(Dependency dependency){
6           this.dependency = dependency;
7       }
8   
9       // 用于测试验证dependency是否被注入
10      public Dependency getDependency() {
11          return dependency;
12      }
13  }
```

创建 DependencyNotFoundException 异常类

```java
1   public class DependencyNotFoundException extends RuntimeException {
2   }
```

运行测试，会抛异常：

```java
1   Caused by: java.lang.NullPointerException: Cannot invoke "jakarta.inject.Provider.get()" because the return value of "java.util.Map.get(Object)" is null
2   	at world.nobug.tdd.di.Context.get(Context.java:52)
3   	at world.nobug.tdd.di.Context.lambda$bind$1(Context.java:27)
4   	at java.base/java.util.stream.ReferencePipeline$3$1.accept(ReferencePipeline.java:197)
5   	at java.base/java.util.Spliterators$ArraySpliterator.forEachRemaining(Spliterators.java:992)
6   	at java.base/java.util.stream.AbstractPipeline.copyInto(AbstractPipeline.java:509)
7   	at java.base/java.util.stream.AbstractPipeline.wrapAndCopyInto(AbstractPipeline.java:499)
8   	at java.base/java.util.stream.AbstractPipeline.evaluate(AbstractPipeline.java:575)
9   	at java.base/java.util.stream.AbstractPipeline.evaluateToArrayNode(AbstractPipeline.java:260)
10  	at java.base/java.util.stream.ReferencePipeline.toArray(ReferencePipeline.java:616)
11  	at world.nobug.tdd.di.Context.lambda$bind$3(Context.java:28)
```

## [](#实现 "实现")实现

根据以上的异常，定位到的问题是：

```java
1   public <Type> Type get(Class<Type> type) {
2       return (Type) providers.get(type).get();
3   }
```

注入依赖时，需要先 get 到对应依赖的实例，但是当前没有实例，这里会抛 NullPointerException 异常。

快速的实现方式是在 get 时校验实例是否存在：

```java
1   public <Type> Type get(Class<Type> type) {
2       if (!providers.containsKey(type)) throw new DependencyNotFoundException();
3       return (Type) providers.get(type).get();
4   }
```

注意，在 bind 方法中，需要修改软化异常的代码，仅将跟反射调用相关的异常软化为 RuntimeException

![image-20240809161723867](~/assets/images/spring-di/image-20240809161723867.png)

# [](#TODO-component-does-not-exist "TODO: component does not exist")TODO: component does not exist

基于前面的测试，我们还可以想到有直接获取组件的情况。

上一个测试用例是通过依赖关系去组件不存在的情况，这个测试用例是直接取组件但是不存在的情况。

## [](#构造测试-7 "构造测试")构造测试

在这个场景下，get 方法会返回 DependencyNotFoundException 异常，因为这个 get 方法也是一个直接对外的 API，直接抛 DependencyNotFoundException 很多时候都不太合理，而且这个异常的名称也不太合理。

按目前的编程风格，我们更倾向于这种情况返回一个 null，返回一个 Optional

```java
1   // TODO: component does not exist
2   @Test
3   public void should_() {
4       Optional<Component> component = context.get_(Component.class);
5   }
```

上面的代码调用的是 `get_`，因为 get 方法在即对外开放也被内部多个地方调用，并且返回值也发生了变化，所以考虑定义一个新的方法。

这么做的化其实也是为了适应测试的需要在做重构。

## [](#为测试做重构 "为测试做重构")为测试做重构

第一步，新建 get\_ 方法：

```java
1   public <Type> Type get(Class<Type> type) {
2       if (!providers.containsKey(type)) throw new DependencyNotFoundException();
3       return (Type) providers.get(type).get();
4   }
5   
6   // 签名原来的 get 方法保持一致就可以了
7   public <Type> Optional<Type> get_(Class<Type> type) {
8       return null;
9   }
```

第二步，基于这个 get\_ 方法，重构测试：

```java
1   // TODO: component does not exist
2   @Test
3   public void should_return_empty_if_component_not_defined() {
4       Optional<Component> component = context.get_(Component.class);
5       assertTrue(component.isEmpty());
6   }
```

## [](#实现-1 "实现")实现

第一步，修改 get\_ 方法

```java
1   public <Type> Optional<Type> get_(Class<Type> type) {
2       return Optional.ofNullable(providers.get(type)).map(provider -> (Type)provider.get());
3   }
```

运行测试，所有测试通过。

第二步，修改 get 方法，将 get 方法的实现委托给 get\_ 方法：

```java
1   public <Type> Type get(Class<Type> type) {
2       return get_(type).orElseThrow(DependencyNotFoundException::new);
3   }
```

第三步，inline get 方法，即可以将 get 方法移除掉

第四步，将 get\_ 方法重命名为 get

第五步，移除部分 get 方法后的 `.orElseThrow()` ，修改为 `.get()`

# [](#TODO：-cyclic-dependencies "TODO： cyclic dependencies")TODO： cyclic dependencies

循环依赖的场景

希望在出现循环依赖时抛出指示循环依赖的异常

## [](#直接循环依赖 "直接循环依赖")直接循环依赖

A -> B -> A

### [](#构造测试-8 "构造测试")构造测试

这个 DependencyDependedOnComponent 依赖于 Component

```java
1   class DependencyDependedOnComponent implements Dependency{
2       private Component component;
3   
4       @Inject
5       public DependencyDependedOnComponent(Component component){
6           this.component = component;
7       }
8   }
```

```java
1   // TODO： cyclic dependencies
2   @Test
3   public void should_throw_exception_if_cyclic_dependencies() {
4       context.bind(Component.class, ComponentWithInjectConstructor.class);
5       context.bind(Dependency.class, DependencyDependedOnComponent.class);
6   
7       assertThrows(CyclicDependenciesException.class, () -> context.get(Component.class));
8   }
```

运行测试，抛出如下 StackOverflowError 异常：

```java
1   Caused by: java.lang.StackOverflowError
2   	at java.base/java.lang.reflect.Executable.getParameters(Executable.java:370)
3   	at world.nobug.tdd.di.Context.lambda$bind$3(Context.java:28)
4   	at world.nobug.tdd.di.Context.lambda$get$6(Context.java:54)
5   	at java.base/java.util.Optional.map(Optional.java:260)
6   	at world.nobug.tdd.di.Context.get(Context.java:54)
7   	at world.nobug.tdd.di.Context.lambda$bind$1(Context.java:29)
8   	at java.base/java.util.stream.ReferencePipeline$3$1.accept(ReferencePipeline.java:197)
9   	at java.base/java.util.Spliterators$ArraySpliterator.forEachRemaining(Spliterators.java:992)
10  	at java.base/java.util.stream.AbstractPipeline.copyInto(AbstractPipeline.java:509)
11  	at java.base/java.util.stream.AbstractPipeline.wrapAndCopyInto(AbstractPipeline.java:499)
12  	at java.base/java.util.stream.AbstractPipeline.evaluate(AbstractPipeline.java:575)
```

出现这个异常的原因是，get 时会去递归调用 get 方法用于获取依赖的组件的实例。

### [](#实现-2 "实现")实现

目前创建组件实例方式，是通过在 bind 时 put 一个类型对应的 Provider 工厂，并在 get 时使用这个工厂来创建实例。

在目前的情况下，我们是无法知道哪个哪个实例正在创建中的，所以就会一直递归执行 get 方法。

我们预期的实现方式是为需要构造的组件增加一个正在构造的标记，那么当第二次尝试构造这个组件时发现这个组件正在构造，那么就产生了循环依赖。

在我们的实现中是使用匿名的 Provider 来 new 对象。那么如果我们能识别出访问过两次同一个 Provider，那么就产生了循环依赖。

这里需要做的就是将匿名的 Provider，变成具体的类，并在这个类上保持一个是否正在创建的标志。

#### [](#重构-2 "重构")重构

将 bind 方法中的匿名内部类创建方法提取为函数

```java
1   public <Type, Implementation extends Type>
2   void bind(Class<Type> type, Class<Implementation> implementation) {
3       Constructor<Implementation> injectConstructor = getInjectConstructor(implementation);
4   
5       providers.put(type, getTypeProvider(injectConstructor));
6   }
7   
8   private <Type> Provider<Object> getTypeProvider(Constructor<Type> injectConstructor) {
9       return () -> getImplementation(injectConstructor); // 预期将变成，new xxxx(injectConstructor)的形式
10  }
11  
12  private <Type> Type getImplementation(Constructor<Type> injectConstructor) {
13      try {
14          // 根据构造函数的参数，获取依赖的实例
15          Object[] dependencies = Arrays.stream(injectConstructor.getParameters())
16                  .map(p -> get(p.getType()).orElseThrow(DependencyNotFoundException::new))
17                  .toArray(Object[]::new);
18          return injectConstructor.newInstance(dependencies);
19      } catch (InvocationTargetException | InstantiationException | IllegalAccessException e) {
20          throw new RuntimeException(e);
21      }
22  }
```

#### [](#重构-3 "重构")重构

新建 Provider 的实现类：ConstructorInjectionProvider

```java
1   class ConstructorInjectionProvider<T> implements Provider<T>{
2       private Constructor<T> injectConstructor;
3   
4       public ConstructorInjectionProvider(Constructor<T> injectConstructor) {
5           this.injectConstructor = injectConstructor;
6       }
7   
8       @Override
9       public T get() {
10          return getImplementation(injectConstructor);
11      }
12  }
```

修改获取 Provider 的方法

```java
1   private <Type> Provider<Object> getTypeProvider(Constructor<Type> injectConstructor) {
2       return new ConstructorInjectionProvider(injectConstructor); // 变成，new xxxx(injectConstructor)的形式
3   }
```

运行测试，依然之后循环依赖的代码失败。

inline 提取的方法:

```java
1   public <Type, Implementation extends Type>
2   void bind(Class<Type> type, Class<Implementation> implementation) {
3       Constructor<Implementation> injectConstructor = getInjectConstructor(implementation);
4   
5       providers.put(type, new ConstructorInjectionProvider(injectConstructor));
6   }
7   
8   class ConstructorInjectionProvider<T> implements Provider<T>{
9       private Constructor<T> injectConstructor;
10  
11      public ConstructorInjectionProvider(Constructor<T> injectConstructor) {
12          this.injectConstructor = injectConstructor;
13      }
14  
15      @Override
16      public T get() {
17          try {
18              // 根据构造函数的参数，获取依赖的实例
19              Object[] dependencies = Arrays.stream(injectConstructor.getParameters())
20                      .map(p -> Context.this.get(p.getType()).orElseThrow(DependencyNotFoundException::new))
21                      .toArray(Object[]::new);
22              return injectConstructor.newInstance(dependencies);
23          } catch (InvocationTargetException | InstantiationException | IllegalAccessException e) {
24              throw new RuntimeException(e);
25          }
26      }
27  }
```

#### [](#实现-3 "实现")实现

在 Provider 的实现类 ConstructorInjectionProvider 中增加 constructing标志位，以指示是否在构建中，并实现循环依赖的检测：

```java
1   class ConstructorInjectionProvider<T> implements Provider<T>{
2       private Constructor<T> injectConstructor;
3       private boolean constructing = false;
4   
5       public ConstructorInjectionProvider(Constructor<T> injectConstructor) {
6           this.injectConstructor = injectConstructor;
7       }
8   
9       @Override
10      public T get() {
11          // 如果在构建中就抛异常
12          if (constructing) throw new CyclicDependenciesException();
13          try {
14              constructing = true;
15              // 根据构造函数的参数，获取依赖的实例
16              Object[] dependencies = Arrays.stream(injectConstructor.getParameters())
17                      .map(p -> Context.this.get(p.getType()).orElseThrow(DependencyNotFoundException::new))
18                      .toArray(Object[]::new);
19              return injectConstructor.newInstance(dependencies);
20          } catch (InvocationTargetException | InstantiationException | IllegalAccessException e) {
21              throw new RuntimeException(e);
22          } finally {
23              constructing = false;
24          }
25      }
26  }
```

## [](#传递性的循环依赖 "传递性的循环依赖")传递性的循环依赖

A -> B -> C -> A

### [](#构造测试-9 "构造测试")构造测试

```java
1   @Test // A -> B -> C -> A
2   public void should_throw_exception_if_transitive_cyclic_dependencies() {
3       context.bind(Component.class, ComponentWithInjectConstructor.class);
4       context.bind(Dependency.class, DependencyDependedOnAnotherDependency.class);
5       context.bind(AnotherDependency.class, AnotherDependencyDependedOnComponent.class);
6   
7       assertThrows(CyclicDependenciesException.class, () -> context.get(Component.class));
8   }
```

新增两个测试类

```java
1   class AnotherDependencyDependedOnComponent implements AnotherDependency{
2       private Component component;
3   
4       @Inject
5       public AnotherDependencyDependedOnComponent(Component component){
6           this.component = component;
7       }
8   }
9   
10  class DependencyDependedOnAnotherDependency implements Dependency{
11      private AnotherDependency anotherDependency;
12  
13      @Inject
14      public DependencyDependedOnAnotherDependency(AnotherDependency anotherDependency){
15          this.anotherDependency = anotherDependency;
16      }
17  }
```

运行测试，所有测试依然可以通过。

# [](#重构-4 "重构")重构

## [](#整理代码位置 "整理代码位置")整理代码位置

移动代码的位置，使容器的接口都集中到一起。

![image-20240809184214486](~/assets/images/spring-di/image-20240809184214486.png)

# [](#优化异常信息 "优化异常信息")优化异常信息

从API的角度来看，目前的异常处理部分返回的信息并不清晰，作为一个使用者，希望能从异常中获取到更多的有效信息。

## [](#DependencyNotFoundException "DependencyNotFoundException")DependencyNotFoundException

对于依赖不存在的情况，使用者希望明确知道是哪个依赖不存在。

### [](#直接依赖缺失的情况 "直接依赖缺失的情况")直接依赖缺失的情况

修改测试用例，在异常中增加缺失的依赖的信息

```java
1   // dependencies not exist
2   @Test
3   public void should_throw_exception_if_dependency_not_found() {
4       context.bind(Component.class, ComponentWithInjectConstructor.class);
5   
6       DependencyNotFoundException exception = assertThrows(DependencyNotFoundException.class, () -> {
7           context.get(Component.class).get();
8       });
9   
10      assertEquals(Dependency.class, exception.getDependency());
11  }
```

修改 DependencyNotFoundException 以适应需求

```java
1   public class DependencyNotFoundException extends RuntimeException {
2       private Class<?> dependency;
3   
4       public DependencyNotFoundException(Class<?> dependency) {
5           this.dependency = dependency;
6       }
7   
8       public Class<?> getDependency() {
9           return dependency;
10      }
11  }
```

修改异常的定义后，需要修改抛出异常时的创建代码:

![image-20240809185759277](~/assets/images/spring-di/image-20240809185759277.png)

编译通过后，运行测试，所有测试都通过。

### [](#传递性中的依赖缺失的情况 "传递性中的依赖缺失的情况")传递性中的依赖缺失的情况

新增一个测试

```java
1   @Test
2   public void should_throw_exception_if_transitive_dependency_not_found() {
3       context.bind(Component.class, ComponentWithInjectConstructor.class);
4       context.bind(Dependency.class, DependencyWithInjectConstructor.class); // 缺失 String 类型的依赖
5   
6       DependencyNotFoundException exception = assertThrows(DependencyNotFoundException.class, () -> {
7           context.get(Component.class);
8       });
9   
10      assertEquals(String.class, exception.getDependency());
11  }
```

在这种情况下，DependencyNotFoundException 异常中，只能返回缺失的依赖是哪个，但是并不知道是哪个组件缺失依赖。

所以，使用者还希望在 DependencyNotFoundException 中获取到缺失依赖的组件的信息。

修改测试代码，异常中增加缺失依赖的组件的信息：

![image-20240809191402158](~/assets/images/spring-di/image-20240809191402158.png)

修改 DependencyNotFoundException，增加 component 属性信息和构造函数

```java
1   public class DependencyNotFoundException extends RuntimeException {
2       private Class<?> dependency;
3       private Class<?> component;
4   
5       public DependencyNotFoundException(Class<?> dependency) {
6           this.dependency = dependency;
7       }
8   
9       public DependencyNotFoundException(Class<?> component, Class<?> dependency) {
10          this.dependency = dependency;
11          this.component = component;
12      }
13  
14      public Class<?> getDependency() {
15          return dependency;
16      }
17  
18      public Class<?> getComponent() {
19          return component;
20      }
21  }
```

通过 Find Usages 找到，单个参数的构造函数在哪里被使用，这里是只被一处地方使用，我们现在需要将使用的地方修改为使用两个参数的构造函数

> 如果有多个地方使用了这个构造函数的话，建议通过工厂方法的方式替换掉这个构造函数

在抛出异常时返回缺失依赖的组件信息，由于创建 ConstructorInjectionProvider 时并没有传入组件的信息

所以需要修改 ConstructorInjectionProvider 记录组件的信息，在其中增加 componentType 字段信息，并相应的修改必要代码

![image-20240809194930682](~/assets/images/spring-di/image-20240809194930682.png)

> 另外一种可行的方案是直接通过 injectConstructor 的 getDeclaringClass 方法，返回该构造器所属的类。
> 
> ![Snipaste_2024-08-09_19-43-11](~/assets/images/spring-di/Snipaste_2024-08-09_19-43-11.png)
> 
> 但是这个方法返回的就不是 Dependency，而是其子类 DependencyWithInjectConstructor
> 
> ```plaintext
> 1   Expected :interface world.nobug.tdd.di.Dependency
> 2   Actual   :class world.nobug.tdd.di.DependencyWithInjectConstructor
> ```
> 
> 如果使用这个方法的话就需要修改测试为：
> 
> ```java
> 1   assertEquals(DependencyWithInjectConstructor.class, exception.getComponent());
> ```
> 
> 我们是将 DependencyWithInjectConstructor 绑定到 Dependency
> 
> ```java
> 1   context.bind(Dependency.class, DependencyWithInjectConstructor.class); 
> ```
> 
> 所以，最好还是校验：
> 
> ```java
> 1   assertEquals(Dependency.class, exception.getComponent());
> ```

## [](#CyclicDependenciesException "CyclicDependenciesException")CyclicDependenciesException

同理，和 DependencyNotFoundException 类似，使用者希望从循环依赖异常中获得更多的异常信息，比如是哪两个组件之间出现了循环依赖或引发循环依赖的组件是哪一个。

```java
1   @Test // A -> B -> A
2   public void should_throw_exception_if_cyclic_dependencies() {
3       context.bind(Component.class, ComponentWithInjectConstructor.class);
4       context.bind(Dependency.class, DependencyDependedOnComponent.class);
5   
6       CyclicDependenciesException exception =
7               assertThrows(CyclicDependenciesException.class, () -> context.get(Component.class));
8   
9       Set<Class<?>> classes = Sets.newSet(exception.getComponents());
10  
11      assertEquals(2, classes.size());
12      assertTrue(classes.contains(Component.class));
13      assertTrue(classes.contains(Dependency.class));
14  }
```

修改异常，在异常中增加组件相互循环依赖的组件信息

```java
1   public class CyclicDependenciesException extends RuntimeException{
2   
3       public Class<?>[] getComponents() {
4           return new Class<?>[0]; // 并没有实际的功能，只是为了使编译通过
5       }
6   }
```

find usages 发现，只有在 Provider 的 get 方法中会抛出循环依赖的异常，那么需要在抛出异常时传入当前类型的信息

![image-20240810095457438](~/assets/images/spring-di/image-20240810095457438.png)

修改异常类，创建构造函数，并增加保存循环依赖的容器

```java
1   public class CyclicDependenciesException extends RuntimeException{
2       private Set<Class<?>> components = new HashSet<>();
3   
4       public CyclicDependenciesException(Class<?> componentType) {
5           components.add(componentType);
6       }
7   
8       public Class<?>[] getComponents() {
9           return components.toArray(Class<?>[]::new);
10      }
11  }
```

又因为，get 方法是一个递归调用的方法，所以第一次抛出循环依赖的异常是内层的 get 方法抛出的，那么外层的 get 方法不能吞掉/软化循环依赖的异常，并且需要在这个异常中增加外层的组件类型信息。

![image-20240810101133637](~/assets/images/spring-di/image-20240810101133637.png)

```java
1   public class CyclicDependenciesException extends RuntimeException{
2       private Set<Class<?>> components = new HashSet<>();
3   
4       public CyclicDependenciesException(Class<?> componentType) {
5           components.add(componentType);
6       }
7   
8       public CyclicDependenciesException(Class<?> componentType, Class<?>[] components) {
9           this.components.add(componentType);
10          this.components.addAll(Set.of(components));
11      }
12  
13      public Class<?>[] getComponents() {
14          return components.toArray(Class<?>[]::new);
15      }
16  }
```

补全具有传递性依赖的测试：

```java
1   @Test // A -> B -> C -> A
2   public void should_throw_exception_if_transitive_cyclic_dependencies() {
3       context.bind(Component.class, ComponentWithInjectConstructor.class);
4       context.bind(Dependency.class, DependencyDependedOnAnotherDependency.class);
5       context.bind(AnotherDependency.class, AnotherDependencyDependedOnComponent.class);
6   
7       CyclicDependenciesException exception =
8               assertThrows(CyclicDependenciesException.class, () -> context.get(Component.class));
9   
10      List<Class<?>> components = Arrays.stream(exception.getComponents()).toList();
11  
12      assertEquals(3, components.size());
13      assertTrue(components.contains(Component.class));
14      assertTrue(components.contains(Dependency.class));
15      assertTrue(components.contains(AnotherDependency.class));
16  }
```

# [](#将依赖的检查提前到获取实例之前 "将依赖的检查提前到获取实例之前")将依赖的检查提前到获取实例之前

目前对循环依赖的检查是在调用 get 方法从容器中获取实例时触发的，更好的方式是在 bind 时就校验是否存在循环依赖。

如果直接在 bind 中检查循环依赖的话，那么在当前类型在 bind 时必须保证其依赖的类型先被 bind，但是这对 API 的使用者来说是很不友好的，这样会要求使用者必须自己控制相互依赖的类型的 bind 顺序。

> 通常我们对于IOC容器的要求是：根据配置文件构建容器上下文之后，很少进行修改。
> 
> IOC 容器是有一个明确的生命周期的，所有配置文件都被 load 好了，然后把容器 build 出来，一但上下文 build 好了，很少要求对上下文进行修改。

**所以还是要在获取容器时检查依赖。**

所以预期修改后的结果大致是，从 context 中 get 一个 container，再从 container 中获取实例。

这个时候 context 就类似于一个 configuration。

这样就将构造的环境和真正构造好的对象的使用环节分开了，就是利用构造器模式来解决这个问题。

## [](#重构-将-Builder-和-Context-上下文分开 "重构-将 Builder 和 Context 上下文分开")重构-将 Builder 和 Context 上下文分开

将 Context 改名为 ContextConfig

### [](#移动-get-方法 "移动 get 方法")移动 get 方法

接着需要将 get 方法从 Context 中移动到其他地方，因为现在 ContextConfig 是要作为一个配置文件，不应该包含 get 实例的方法。

> bind 方法可以视为设置配置文件的操作

最简单的做法是，先将 ContextConfig 实现一个 Context 接口

> 因为在我们当前的代码中，ContextConfig 即是配置文件也是上下文容器本身。

```java
1   public class ContextConfig implements Context {
2       ......
3   }
```

创建 Context 接口

```java
1   public interface Context {
2   }
```

接着需要将 get 方法挪到 Context 接口中去

使用 Pull Members Up 重构方法，来挪动

![image-20240810110504080](~/assets/images/spring-di/image-20240810110504080.png)

![image-20240810110639340](~/assets/images/spring-di/image-20240810110639340.png)

挪动之后，Context 接口的变化：

```java
1   public interface Context {
2       <Type> Optional<Type> get(Class<Type> type);
3   }
```

![image-20240810110805138](~/assets/images/spring-di/image-20240810110805138.png)

接下来需要做的就是，让 get 方法不再直接调用 contextConfig 的内容，即需要将 get 方法从 config 中移除掉，但同时还要保持现在的功能。

第一查找替换的方式重构

创建一个获取 Context 的方法，这样才能在

> 预期要做的就是将 Context 中的 get 方法实现为和当前 ContextConfig 中的 get 方法一致。

```java
1   public Context getContext() {
2       return new Context() {
3           @Override
4           public <Type> Optional<Type> get(Class<Type> type) {
5               return Optional.empty();
6           }
7       };
8   }
```

将 get 方法的实现提取为方法：

```java
1   @Override
2   public <Type> Optional<Type> get(Class<Type> type) {
3       return getType(type);
4   }
5   
6   private <Type> Optional<Type> getType(Class<Type> type) {
7       return Optional.ofNullable(providers.get(type)).map(provider -> (Type) provider.get());
8   }
```

将 getContext 方法的实现委托给上一步提取的 getType 方法

```java
1   public Context getContext() {
2       return new Context() {
3           @Override
4           public <Type> Optional<Type> get(Class<Type> type) {
5               return getType(type);
6           }
7       };
8   }
```

inline 掉 getType 方法，这样 getContext 中的实现方法，就和 get 方法一致了

```java
1   public Context getContext() {
2       return new Context() {
3           @Override
4           public <Type> Optional<Type> get(Class<Type> type) {
5               return Optional.ofNullable(providers.get(type)).map(provider -> (Type) provider.get());
6           }
7       };
8   }
9   
10  @Override
11  public <Type> Optional<Type> get(Class<Type> type) {
12      return Optional.ofNullable(providers.get(type)).map(provider -> (Type) provider.get());
13  }
```

再将 get 方法的实现委给 getContext 方法：

```java
1   @Override
2   public <Type> Optional<Type> get(Class<Type> type) {
3       return getContext().get(type);
4   }
```

接着可以移除掉 get 方法的 Override，也移除掉 ContextConfig 需要实现的接口：

![](~/assets/images/spring-di/Snipaste_2024-08-10_11-36-38.png)

![image-20240810113656568](~/assets/images/spring-di/image-20240810113656568.png)

接着，inline 掉 get 方法，那么之前使用 get 方法的地方都变成了调用 `getContext().get(type)`

![Snipaste_2024-08-10_11-39-45](~/assets/images/spring-di/Snipaste_2024-08-10_11-39-45.png)

那么，ContextConfig 中就只剩下两个 bind 方法，和 getContext 方法，这样就无法在修改上下文了。

这样，ContextConfig 就符合了我们将其用于配置上下文的要求。

这样就调整了它对外的接口，并将实现了 Config 和实际的 Context 容器的使用做了分离。

## [](#目前存在的问题 "目前存在的问题")目前存在的问题

经过上面的重构，就可以在 getContext 来进行必要的检查，比如**检查循环依赖、依赖是否有缺失**，等等情况。

当前，在 Provider 内部需要为当前组件注入依赖时，都需要从容器中查找依赖的实例（获取容器的方式都是调用 getContext 方法），但是，现在 getContext 时都会创建一个新的 Context，这不符合实际使用的要求。

![image-20240810115120039](~/assets/images/spring-di/image-20240810115120039.png)

但是当前并不能从 Provider 中获取到容器上下文的实例，并且也无法在创建 Provider 时传入容器实例（此时容器还未创建）

那么只能通过在调用 get 方法时，传入已经存在的 Context

但是我们现在实现的 Provider 是 `jakarta.inject.Provider` 其中的 get 方法是一个无参方法，无法满足我们的需求，那么我们就需要创建一个有参的函数式接口。

### [](#新建-Provider-接口 "新建 Provider 接口")新建 Provider 接口

```java
1   interface ComponentProvider<T> {
2       T get(Context context);
3   }
```

创建完之后，需要使用这个 ComponentProvider 来替换所有用到 Provider 的地方。

最直接的修改方式就是 人工手动的来做这个替换。

如果一定要按照严格的重构去做的话就需要平行的一步步替换，即先增加并逐步替换掉功能，再移除掉旧的功能。

**使用重构式的方式可以保证在代码量比较大的时候仍然能使代码修改成功。**

### [](#逐步重构 "逐步重构")逐步重构

新建一个 componentProviders

```java
1   private Map<Class<?>, Provider<?>> providers = new HashMap<>();
2   private Map<Class<?>, ComponentProvider<?>> componentProviders = new HashMap<>();
```

修改 bind 的方法：

```java
1   public <Type> void bind(Class<Type> type, Type instance) {
2       providers.put(type, () -> instance);
3       componentProviders.put(type, context -> instance);
4   }
5   
6   public <Type, Implementation extends Type>
7   void bind(Class<Type> type, Class<Implementation> implementation) {
8       Constructor<Implementation> injectConstructor = getInjectConstructor(implementation);
9   
10      providers.put(type, new ConstructorInjectionProvider(type, injectConstructor));
11      componentProviders.put(type, new ConstructorInjectionProvider(type, injectConstructor));
12  }
```

修改 ConstructorInjectionProvider 的实现，通过实现两个接口来实现后续的平行替换。

![image-20240812095213493](~/assets/images/spring-di/image-20240812095213493.png)

将 get 方法的实现提取为函数 getT，并将里面的 getContext() 抽取为函数参数

> 使用 Ctrl + Alt + P 将 getContext() 提取为参数

那么 ComponentProvider 的实现如下：

```java
1   @Override
2   public T get(Context context) {
3       return getT(context);
4   }
```

接着，将 getT 方法 inline 并将 Provider 的实现修改为委托给 ComponentProvider 的 get 方法：

ComponentProvider 的 get 方法 inline：

![image-20240812100841607](~/assets/images/spring-di/image-20240812100841607.png)

```java
1   @Override
2   public T get() {
3       return get(getContext());
4   }
5   
6   @Override
7   public T get(Context context) {
8       if (constructing) throw new CyclicDependenciesException(componentType);
9       try {
10          constructing = true;
11          // 根据构造函数的参数，获取依赖的实例
12          Object[] dependencies = Arrays.stream(injectConstructor.getParameters())
13                  .map(p -> {
14                      Class<?> type = p.getType();
15                      return context.get(type)
16                              .orElseThrow(() -> new DependencyNotFoundException(
17                                      componentType, p.getType()));
18                  })
19                  .toArray(Object[]::new);
20          return injectConstructor.newInstance(dependencies);
21      } catch (CyclicDependenciesException e) {
22          Class<?>[] components = e.getComponents();
23          throw new CyclicDependenciesException(componentType, components);
24      } catch (InvocationTargetException | InstantiationException | IllegalAccessException e) {
25          throw new RuntimeException(e);
26      } finally {
27          constructing = false;
28      }
29  }
```

> inline getT 方法后，getT 方法就没有地方使用了，可以删除了

接着，移除掉所有使用 providers 的代码

```java
1   private Map<Class<?>, Provider<?>> providers = new HashMap<>();
```

并将容器中的 Provider 改为 componentProviders，并在 get 时，传入当前的容器上下文 Context

![Snipaste_2024-08-12_10-27-52](~/assets/images/spring-di/Snipaste_2024-08-12_10-27-52.png)

经过上面的重构，我们已经具备了在 bind 时检查依赖的能力。

这里还可以将 componProviders 重命名为 providers

## [](#在获取容器时检查依赖缺失的情况 "在获取容器时检查依赖缺失的情况")在获取容器时检查依赖缺失的情况

目前对依赖缺失的检查是在 get 时进行的。

![image-20240812104907259](~/assets/images/spring-di/image-20240812104907259.png)

### [](#构造测试-10 "构造测试")构造测试

那么，需要在获取容器时时检查，只需要将 `.get(Component.class)` 方法移除就可以了

> 注意，这里可以同时修改传递性依赖缺失的测试用例
> 
> ![Snipaste_2024-08-12_11-40-11](~/assets/images/spring-di/Snipaste_2024-08-12_11-40-11.png)

移除后运行测试，测试不通过：

```plaintext
1   org.opentest4j.AssertionFailedError: Expected world.nobug.tdd.di.DependencyNotFoundException to be thrown, but nothing was thrown.
```

### [](#快速实现-5 "快速实现")快速实现

需要在 getContext 时检查依赖：

![image-20240812110730534](~/assets/images/spring-di/image-20240812110730534.png)

实现：在 bind 时同时记录注册的组件需要哪些依赖的类型，并在创建 Context 之前校验所有组件的依赖的类型是否都已经注册到容器中了

新建一个字段记录组件的依赖：

```java
1   private Map<Class<?>, List<Class<?>>> dependencies = new HashMap<>();
```

在 bind 时记录组件需要的依赖的类型：

![image-20240812111635721](~/assets/images/spring-di/image-20240812111635721.png)

在创建容器上下文之前，先检查所有注册的组件所需要的所有依赖是否都已经注册到容器中:

![image-20240812112111509](~/assets/images/spring-di/image-20240812112111509.png)

```java
1   for (Class<?> component : dependencies.keySet()) { // 遍历所有需要注册到容器中的组件
2       for (Class<?> dependency : dependencies.get(component)) { // 获取当前遍历的组件的所有依赖的类型，并遍历这些依赖的类型
3           if (!componentProviders.containsKey(dependency)) // 检查容器中是否已经注册了这些依赖的类型
4               throw new DependencyNotFoundException(component, dependency);
5       }
6   }
```

> 在没有循环依赖的情况下，直接检查依赖的类型是否注册到容器是有效的。

同理，对于间接的依赖缺失的测试，也需要修改

![Snipaste_2024-08-12_11-40-11](~/assets/images/spring-di/Snipaste_2024-08-12_11-40-11.png)

移除`.get(Component.class)` ，运行测试，测试也会通过。

## [](#简单重构-简化命名 "简单重构-简化命名")简单重构-简化命名

将 componentProviders 重命名为 providers

将 contextConfig 重命名为 config

## [](#在获取容器时检查循环依赖的情况 "在获取容器时检查循环依赖的情况")在获取容器时检查循环依赖的情况

### [](#构造测试-11 "构造测试")构造测试

同理这里也是需要移除`.get(Component.class)`

> 循环依赖的测试也有两个，一个是直接循环依赖，一个是间接/传递循环依赖，都需要修改测试

### [](#快速实现-6 "快速实现")快速实现

这里的实现原理就是基于图算法：给定一个图的连接表，寻找图上是否存在环。

深度优先遍历，检查是否会重复回到某个节点。

```java
1   // 深度优先遍历 检查 component 的依赖的访问记录
2   // visiting 保存正在被访问的记录，如果发现正在被访问的记录再次被访问，说明存在循环依赖
3   private void checkDependencies(Class<?> component, Stack<Class<?>> visiting) {
4       for (Class<?> dependency : dependencies.get(component)) {
5           if (visiting.contains(dependency)) throw new CyclicDependenciesException(visiting);
6           visiting.push(dependency);
7           checkDependencies(dependency, visiting);
8           visiting.pop();
9       }
10  }
```

getContext 时深度优先遍历，检查每一个组件的依赖链上是否有环

![image-20240812140847037](~/assets/images/spring-di/image-20240812140847037.png)

运行测试，`should_throw_exception_if_transitive_dependency_not_found` 会有空指针异常，异常发生在

![image-20240812142838411](~/assets/images/spring-di/image-20240812142838411.png)

因为在这个测试中，String 类型并没有注册到容器中，即没有执行 `bind(String.class, "Hello")`方法，所以递归到 `dependencies.get(String.class)` 时，会返回 null，就会引发空指针异常。

修改，提前判断依赖是否存在，如果不存在就不必再进行下一步的递归了，避免了空指针异常。

![Snipaste_2024-08-12_14-42-35](~/assets/images/spring-di/Snipaste_2024-08-12_14-42-35.png)

那么以下的代码，就是重复了，可以移除了

![image-20240812144651351](~/assets/images/spring-di/image-20240812144651351.png)

将 for 循环的代码改成 foreach 形式

![Snipaste_2024-08-12_14-50-35](~/assets/images/spring-di/Snipaste_2024-08-12_14-50-35.png)

## [](#移除获取实例时（get时）往外抛异常的代码 "移除获取实例时（get时）往外抛异常的代码")移除获取实例时（get时）往外抛异常的代码

因为在创建容器前就已经做了依赖相关的检查，所以就不需要在 ConstructorInjectionProvider 的 get 方法中再往外抛异常了

![image-20240812145737955](~/assets/images/spring-di/image-20240812145737955.png)

> 注意，这里移除掉 orElseThrow 后需要调用 get方法，否在会报 IllegalArgumentException。

移掉掉 get 方法中的异常校验后，代码如下：

![Snipaste_2024-08-12_15-02-46](~/assets/images/spring-di/Snipaste_2024-08-12_15-02-46.png)

接着，移除掉异常类中不在使用的构造方法：

![image-20240812150633641](~/assets/images/spring-di/image-20240812150633641.png)

再移除些不在使用的代码：

![Snipaste_2024-08-12_15-09-43](~/assets/images/spring-di/Snipaste_2024-08-12_15-09-43.png)

这个字段现在只在构造方法中使用，也可以移除掉。

# [](#重构-将-dependencies-移入-providers "重构-将 dependencies 移入 providers")重构-将 dependencies 移入 providers

目前，我们可以观察到在providers中添加数据时同步也会在dependencies中添加数据

你会发现 dependencies 和 providers 一直是伴生的，这实际上意味着，dependencies 是 providers 的额外信息。

这就是一个代码的坏味道，我们需要将其重构的更加高内聚，需要将 dependencies 的关系，放回到 providers 当中去。

![Snipaste_2024-08-12_15-15-52](~/assets/images/spring-di/Snipaste_2024-08-12_15-15-52.png)

给 ComponentProvider 接口增加 getDependencies 方法：

```java
1   interface ComponentProvider<T> {
2       T get(Context context);
3   
4       List<Class<?>> getDependencies();
5   }
```

实现接口，绑定实例时，已经无法使用lambda表达式，应该使用匿名类

![image-20240812153821742](~/assets/images/spring-di/image-20240812153821742.png)

修改 ConstructorInjectionProvider 中的 getDependencies 方法的实现，实现为：

![Snipaste_2024-08-12_15-42-40](~/assets/images/spring-di/Snipaste_2024-08-12_15-42-40.png) ![Snipaste_2024-08-12_15-43-10](~/assets/images/spring-di/Snipaste_2024-08-12_15-43-10.png)

通过 提取方法 + inline 的重构方式实现。

接着，需要将使用 dependencies 的地方，修改为通过 providers 来获取。

目前使用到 dependencies 的地方就是在创建容器前对依赖缺失、循环依赖的校验上。

可以观察到 providers 和 dependencies 的 key 是一样的，所以，所有对于 dependencies 的 key 访问都可以修改为对 providers 的 key 访问。

需要修改的代码如下，分别将其修改为对 providers 的调用

> 每改动一处跑一次测试，通过小步持续跑测试的方式是改进

![image-20240812160514288](~/assets/images/spring-di/image-20240812160514288.png)

修改后：

![Snipaste_2024-08-12_16-10-12](~/assets/images/spring-di/Snipaste_2024-08-12_16-10-12.png)

接着需要移除 dependencies，观察发现，目前 dependencies 只会用来保存数据，所以可以直接将其移除。

可以观察到 getInjectConstructor 除了用于构造 ConstructorInjectionProvider 之外，没有其他的用处。

那么，可以将这个方法，移动到 ConstructorInjectionProvider 里面去，然后在其构造函数中直接调用就好了，这也是一种让代码变得高内聚的方式。

使用 Move Members 的重构方式移动

![image-20240812162507968](~/assets/images/spring-di/image-20240812162507968.png)

![Snipaste_2024-08-12_16-26-15](~/assets/images/spring-di/Snipaste_2024-08-12_16-26-15.png)

接着会发现，对这个方法的调用，变成了如下形式：

![Snipaste_2024-08-12_16-26-45](~/assets/images/spring-di/Snipaste_2024-08-12_16-26-45.png)

inline 一下会发现，new ConstructorInjectionProvider 时，调用了一个 ConstructorInjectionProvider 的静态方法，这也是一种很无聊的做法（坏味道）

![image-20240812162800695](~/assets/images/spring-di/image-20240812162800695.png)

那么只需要将 ConstructorInjectionProvider 的构造方法修改为：

```java
1   public ConstructorInjectionProvider(Class<T> component) {
2       this.injectConstructor = getInjectConstructor(component);
3   }
```

# [](#重构-减少ContextConfig的代码量 "重构-减少ContextConfig的代码量")重构-减少ContextConfig的代码量

将 ConstructorInjectionProvider 从 ContextConfig 中移除形成一个新的单元（组件）

![image-20240812164601445](~/assets/images/spring-di/image-20240812164601445.png)

![image-20240812164702951](~/assets/images/spring-di/image-20240812164702951.png)

![Snipaste_2024-08-12_16-51-08](~/assets/images/spring-di/Snipaste_2024-08-12_16-51-08.png)

# [](#Field-Injection "Field Injection")Field Injection

## [](#如何构造测试 "如何构造测试")如何构造测试

> 这节个人感觉比较重要的就是对于同样的功能，在不同上下文环境下对测试风格的选择方式问题。 在某些情况下，不同的风格传递的信息或者说知识是不太一样的。而伴随你不同风格的选择可能直接影响后续功能实现的难易程度。TDD主要的难点还是在于设计，在于你对知识的理解，究竟是以一种怎样的方式呈现出来。

对于重构过后的代码，如何以何种方式来完成测试？

根据不同环境下会有不同的考量，甚至在同样的功能中选择不同风格的测试

> 测试不仅仅是测试，测试中还蕴含着知识的传递

字段注入

*   通过 Inject 标注将字段声明为依赖组件
*   如果组件需要的依赖不存在，则抛出异常
*   如果字段为 final 则抛出异常
*   如果组件间存在循环依赖，则抛出异常

```java
1   // TODO: field injection
2   // TODO: throw exception if dependency not found
3   // TODO: throw exception if filed is final
4   // TODO: throw exception if cyclic dependency
```

我们把 ConstructorInjectionProvider 从 ContextConfig 中分离出来，也可以说我们的架构改变了，原来我们可以说是一个单体的结构，没有组件和组件间的交互。

字段注入应该是有如下形式的类：

```java
1   class ComponentWithFieldInjection {
2       @Inject
3       Dependency dependency;
4   }
```

即，这个类中包含一个被 `@Inject` 标注的字段。

如果还是按照之前的形式构造测试的话，我们会构造出如下测测试：

```java
1   // TODO: field injection
2   @Test
3   public void should_inject_dependency_via_field() {
4       Dependency dependency = new Dependency() {
5       };
6       config.bind(Dependency.class, dependency);
7       config.bind(ComponentWithFieldInjection.class, ComponentWithFieldInjection.class);
8       ComponentWithFieldInjection component = config.getContext().get(ComponentWithFieldInjection.class).get();
9   
10      assertSame(dependency, component.dependency);
11  }
```

但是在之前的课上也讲过，如果你的架构变了，那么你的任务也可以变。也可以用一些更小范围的测试去测。

所以，另外的写法呢就可以是如下形式：

```java
1   @Test
2   public void should_create_component_with_field_injection() {
3       Context context = Mockito.mock(Context.class);
4       Dependency dependency = Mockito.mock(Dependency.class);
5       Mockito.when(context.get(eq(Dependency.class)))
6               .thenReturn(Optional.of(dependency)); // Provider 内部需要使用context.get方法获取依赖
7   
8       ConstructorInjectionProvider<ComponentWithFieldInjection> provider =
9               new ConstructorInjectionProvider<>(ComponentWithFieldInjection.class);
10      ComponentWithFieldInjection component = provider.get(context); // 会返回一个实例
11  
12      assertSame(dependency, component.dependency);
13  }
```

所以，在重构过程中，随着架构的变化，你实现测试的选择也会有所不同。

对比以上两个测试，可以发现，第一个测试是一个更完整的、范围更大的端到端的功能测试，而第二个它更多的是集中在被我们抽离出来的单元本身，从某种意义上来讲，第二个测试更接近传统意义上的单元测试。

这两个测试并没有什么差别，只是选择的粒度和范围不同而已。也就是对功能上下文、功能点进行了进一步分解。

> **并不是功能架构拆分之后，就应该按照更小的粒度来做测试。**
> 
> 因为测试不仅仅是测试，其中还蕴含着功能上下文中的知识，如果使用测试替身的方式构造测试的话，就需要在测试中管理知识，有可能让新人不会很容易理解。
> 
> 所以在构造测试方法时不仅包含测试的成本，也隐含着测试传递的知识。

再看看这两种测试策略在其他的功能上下文中有什么不一样。

```java
1   // TODO: throw exception if dependency not found
2   @Test
3   public void should_throw_exception_if_filed_dependency_not_found() {
4       config.bind(ComponentWithFieldInjection.class, ComponentWithFieldInjection.class);
5   
6       assertThrows(DependencyNotFoundException.class, () -> config.getContext());
7   }
```

如果缩小测试范围，仅针对单元本身做测试的话，测试应该会被构造成如下形式：

```java
1   @Test
2   public void should_include_field_dependency_in_dependencies() {
3       ConstructorInjectionProvider<ComponentWithFieldInjection> provider =
4               new ConstructorInjectionProvider<>(ComponentWithFieldInjection.class);
5   
6       assertArrayEquals(new Class<?>[]{Dependency.class}, provider.getDependencies().toArray(Class<?>[]::new));
7   }
```

为什么是构造成这种形式呢？

从源码我们可知，对依赖的检查，只需要从 provider 的 getDependencies 获取到其**所需的所有的正确的依赖**就可以进行正确的检查了。

> 后续的检查是在 getContext 时，即创建容器时（new 之前）做的，检查时需要获取到每一个组件的依赖。
> 
> 所以只要 getDependencies 能返回正确的结果，那么就可以保证后续依赖缺失和循环依赖检查的代码能正确实现。

![image-20240813102203192](~/assets/images/spring-di/image-20240813102203192.png)

但是目前这个方法只返回了构造函数参数所需的依赖，那么后续实现只需要在这个方法返回中增加 field 中所需的依赖即可。

![image-20240813102811774](~/assets/images/spring-di/image-20240813102811774.png)

> 你会发现，实际上无论是 dependency not found 还是 循环依赖，实际上都是在 ContextConfig 中去实现的。

同理，循环依赖的情况：

```java
1   // TODO: throw exception if cyclic dependency
2   class DependencyWithFieldInjection implements Dependency{
3       @Inject
4       ComponentWithFieldInjection component;
5   }
6   @Test
7   public void should_throw_exception_when_filed_has_cyclic_dependencies() {
8       config.bind(ComponentWithFieldInjection.class, ComponentWithFieldInjection.class);
9       config.bind(Dependency.class, DependencyWithFieldInjection.class);
10  
11      assertThrows(CyclicDependenciesException.class, () -> config.getContext());
12  }
```

> 其实这里 DependencyWithFieldInjection 可以不必实现 Dependency

如果减小测试的粒度，我们会发现循环依赖的测试，其实和依赖不存在的测试是一样的：

> 因为检查依赖不存在和检查循环依赖都是在 checkDependencies 方法中做的

```java
1   @Test
2   public void should_include_field_dependency_in_dependencies_() {
3       ConstructorInjectionProvider<ComponentWithFieldInjection> provider =
4               new ConstructorInjectionProvider<>(ComponentWithFieldInjection.class);
5   
6       assertArrayEquals(new Class<?>[]{Dependency.class}, provider.getDependencies().toArray(Class<?>[]::new));
7   }
```

所以对`TODO: throw exception if dependency not found` 和 `TODO: throw exception if cyclic dependency` 的测试任务可以合并为一个任务，比如：`TODO: provide dependencies information for field injection`，即：依赖中应包含 Inject Field 声明的依赖

```java
1   // TODO: provide dependencies information for field injection
2   @Test
3   public void should_include_field_dependency_in_dependencies() {
4       ConstructorInjectionProvider<ComponentWithFieldInjection> provider =
5               new ConstructorInjectionProvider<>(ComponentWithFieldInjection.class);
6   
7       assertArrayEquals(new Class<?>[]{Dependency.class}, provider.getDependencies().toArray(Class<?>[]::new));
8   }
```

经过取舍，我们选择保留以下的测试：

```java
1   class ComponentWithFieldInjection {
2       @Inject
3       Dependency dependency;
4   }
5   // TODO: field injection
6   @Test
7   public void should_inject_dependency_via_field() {
8       Dependency dependency = new Dependency() {
9       };
10      config.bind(Dependency.class, dependency);
11      config.bind(ComponentWithFieldInjection.class, ComponentWithFieldInjection.class);
12      ComponentWithFieldInjection component = config.getContext().get(ComponentWithFieldInjection.class).get();
13  
14      assertSame(dependency, component.dependency);
15  }
16  
17  // TODO: provide dependencies information for field injection
18  @Test
19  public void should_include_field_dependency_in_dependencies() {
20      ConstructorInjectionProvider<ComponentWithFieldInjection> provider =
21              new ConstructorInjectionProvider<>(ComponentWithFieldInjection.class);
22  
23      assertArrayEquals(new Class<?>[]{Dependency.class}, provider.getDependencies().toArray(Class<?>[]::new));
24  }
```

## [](#实现-should-inject-dependency-via-field "实现 should_inject_dependency_via_field")实现 should\_inject\_dependency\_via\_field

```java
1   // TODO: field injection
2   @Test
3   public void should_inject_dependency_via_field() {
4       Dependency dependency = new Dependency() {
5       };
6       config.bind(Dependency.class, dependency);
7       config.bind(ComponentWithFieldInjection.class, ComponentWithFieldInjection.class);
8       ComponentWithFieldInjection component = config.getContext().get(ComponentWithFieldInjection.class).get();
9   
10      assertSame(dependency, component.dependency);
11  }
```

运行测试，会有因为无法获取到构造函数（NoSuchMethodException）而抛出 IllegalComponentException 异常

![Snipaste_2024-08-13_11-02-35](~/assets/images/spring-di/Snipaste_2024-08-13_11-02-35.png)

首先需要将 ComponentWithFieldInjection 修改为静态内部类

```java
1   static class ComponentWithFieldInjection {
2       @Inject
3       Dependency dependency;
4   }
```

> 这里也可以将这个类定义为最顶层的类，就和前面构造的 Component 、Dependency 一样，那么修改的代码就要少一点。

并且需要使用 `getDeclaredConstructor` 来获取构造函数。

```java
1   return implementation.getDeclaredConstructor();
```

> `ComponentWithFieldInjection` 是一个非静态内部类（即它是在另一个类的内部定义的类，并且不带有 `static` 关键字），它的构造函数需要调用外部类的构造函数。如果是静态内部类，则不需要这样做。

> 对于非静态内部类（即没有使用 `static` 关键字修饰的内部类），其构造函数实际上是私有的，并且会附加一个对外部类实例的引用。这意味着，即使您没有显式定义构造函数，编译器也会为您生成一个私有的构造函数，该构造函数接受一个外部类的实例作为参数。
> 
> 假设您有一个外部类 `OuterClass` 和一个非静态内部类 `ComponentWithFieldInjection`，如下所示：
> 
> ```java
> 1   public class OuterClass {
> 2    private Dependency dependency;
> 3   
> 4    public class ComponentWithFieldInjection {
> 5        private Dependency dependency;
> 6    }
> 7   }
> ```
> 
> 在这种情况下，您不能直接通过 `getConstructor` 获取到 `ComponentWithFieldInjection` 的构造函数，因为该构造函数是私有的，并且它实际上接受一个 `OuterClass` 实例作为参数。
> 
> 为了获取非静态内部类的构造函数，您需要使用 `getDeclaredConstructor` 并且指定参数类型，如下所示：
> 
> ```java
> 1   try {
> 2    Constructor<ComponentWithFieldInjection> constructor =
> 3        OuterClass.class.getDeclaredConstructor(OuterClass.class);
> 4   } catch (NoSuchMethodException e) {
> 5    // 处理异常
> 6   }
> ```
> 
> 请注意，上述代码中的 `getDeclaredConstructor` 要求您知道构造函数的确切签名。由于构造函数是私有的，您还需要调用 `setAccessible(true)` 来允许访问它：
> 
> ```java
> 1   constructor.setAccessible(true);
> ```
> 
> 但是，通常情况下，您并不需要直接通过反射来创建非静态内部类的实例。通常的做法是通过外部类的实例来创建内部类的实例。例如：
> 
> ```java
> 1   OuterClass outerInstance = new OuterClass();
> 2   ComponentWithFieldInjection component = outerInstance.new ComponentWithFieldInjection();
> ```
> 
> 总结一下，对于非静态内部类，您不能直接使用 `getConstructor` 来获取其构造函数，而需要使用 `getDeclaredConstructor` 并且可能需要调用 `setAccessible(true)` 来访问私有构造函数。

> 在Java中，`getDeclaredConstructor`和`getConstructor`都是用于通过反射来获取类的构造函数的方法，但它们之间存在一些重要的区别：
> 
> 1.  **`getConstructor`**:
>     
>     *   这个方法是从`Class`类继承来的，用于获取公开的构造函数。
>     *   它可以获取到类的公共构造函数，包括从父类继承来的构造函数。
>     *   如果类中有多个公共构造函数，你可以通过指定参数类型数组来获取特定的构造函数。
>     *   如果类没有公共构造函数或者没有匹配给定参数类型的构造函数，这个方法会抛出`NoSuchMethodException`。
> 2.  **`getDeclaredConstructor`**:
>     
>     *   这个方法也是从`Class`类继承来的，但它用于获取类中声明的构造函数，无论这些构造函数是否是公共的。
>     *   它可以获取到类本身的构造函数，包括私有的、受保护的、包私有的以及公共的构造函数，但不会获取从父类继承的构造函数。
>     *   同样地，你可以通过指定参数类型数组来获取特定的构造函数。
>     *   如果类中没有声明匹配给定参数类型的构造函数，这个方法会抛出`NoSuchMethodException`。
> 
> ### [](#示例 "示例")示例
> 
> 假设我们有一个类`MyClass`:
> 
> ```java
> 1   public class MyClass {
> 2       private MyClass() { }  // 私有构造函数
> 3       public MyClass(String name) { }  // 公共构造函数
> 4   }
> ```
> 
> 我们可以这样使用这两个方法:
> 
> ```java
> 1   try {
> 2       Class<MyClass> clazz = MyClass.class;
> 3   
> 4       // 获取公共构造函数
> 5       Constructor<MyClass> publicConstructor = clazz.getConstructor(String.class);
> 6   
> 7       // 获取声明的构造函数（包括私有的）
> 8       Constructor<MyClass> declaredPrivateConstructor = clazz.getDeclaredConstructor();
> 9   
> 10      // 访问私有构造函数
> 11      declaredPrivateConstructor.setAccessible(true);
> 12      MyClass instance = declaredPrivateConstructor.newInstance();
> 13  
> 14  } catch (NoSuchMethodException | IllegalAccessException | InstantiationException | InvocationTargetException e) {
> 15      e.printStackTrace();
> 16  }
> ```
> 
> ### [](#总结 "总结")总结
> 
> *   `getConstructor` 主要用于获取类的公共构造函数。
> *   `getDeclaredConstructor` 主要用于获取类中声明的所有构造函数，包括非公共的构造函数。
> 
> 如果你想要获取一个类中的所有构造函数，不论它们的访问级别如何，应该使用`getDeclaredConstructors`方法，而不是单个构造函数的版本。

获取到构造函数之后，就可以创建实例，因为依赖是字段不是构造函数的参数，所以还需要知道有哪些被 `@Inject` 标注的字段

![Snipaste_2024-08-13_11-40-48](~/assets/images/spring-di/Snipaste_2024-08-13_11-40-48.png)

获取到字段，并创建好实例后就需要给字段赋值：

![image-20240813114315788](~/assets/images/spring-di/image-20240813114315788.png)

即，根据依赖的字段的类型，从容器中获取该类型的实例，并赋值到该字段中。

运行测试，测试通过。

## [](#实现-provide-dependencies-information-for-field-injection "实现 provide dependencies information for field injection")实现 provide dependencies information for field injection

```java
1   // TODO: provide dependencies information for field injection
2   @Test
3   public void should_include_field_dependency_in_dependencies() {
4       ConstructorInjectionProvider<ComponentWithFieldInjection> provider =
5               new ConstructorInjectionProvider<>(ComponentWithFieldInjection.class);
6   
7       assertArrayEquals(new Class<?>[]{Dependency.class}, provider.getDependencies().toArray(Class<?>[]::new));
8   }
```

只需要在 getDependencies 方法的返回结果中增加字段注入的依赖：

```java
1   @Override
2   public List<Class<?>> getDependencies() {
3       Stream<? extends Class<?>> b = injectFields.stream().map(Field::getType);
4       Stream<? extends Class<?>> a = Arrays.stream(injectConstructor.getParameters()).map(Parameter::getType);
5       return Stream.concat(a, b).collect(Collectors.toList());
6   }
```

## [](#对-Subclass-的支持 "对 Subclass 的支持")对 Subclass 的支持

新建一个子类：

```java
1   static class SubclassWithFieldInjection extends ComponentWithFieldInjection {
2   }
```

构造测试

```java
1   @Test
2   public void should_inject_dependency_via_superclass_inject_filed() {
3       Dependency dependency = new Dependency() {
4       };
5       config.bind(Dependency.class, dependency);
6       config.bind(SubclassWithFieldInjection.class, SubclassWithFieldInjection.class);
7       SubclassWithFieldInjection component = config.getContext().get(SubclassWithFieldInjection.class).get();
8   
9       assertSame(dependency, component.dependency);
10  }
```

运行测试：

```plaintext
1   Expected :world.nobug.tdd.di.ContainerTest$ComponentConstruction$FieldInjection$2@479cbee5
2   Actual   :null
```

这是因为，当前在取注入的字段时，只取了当前类的字段：

```java
1   private static <T> List<Field> getInjectFields(Class<T> component) {
2       return Arrays.stream(component.getDeclaredFields())
3               .filter(f -> f.isAnnotationPresent(Inject.class)).toList();
4   }
```

实际上，还需要获取到父类的字段，可以通过递归的方式，找到父类的所有的注入字段：

```java
1   private static <T> List<Field> getInjectFields(Class<T> component) {
2       List<Field> injectFields = new ArrayList<>();
3       Class<?> current = component;
4       while (current != Object.class) {
5           injectFields.addAll(Arrays.stream(current.getDeclaredFields())
6                   .filter(f -> f.isAnnotationPresent(Inject.class)).toList());
7           current = current.getSuperclass();
8       }
9       return injectFields;
10  }
```

# [](#Method-Injection "Method Injection")Method Injection

方法注入

*   通过 Inject 标注的方法，其参数为依赖组件
    
*   通过 Inject 标注的无参数方法，会被调用
    
*   按照子类中的规则，覆盖父类中的 Inject 方法
    
*   如果组件需要的依赖不存在，则抛出异常
    
*   如果方法定义类型参数，则抛出异常
    
*   如果组件间存在循环依赖，则抛出异常
    

方法测试的任务列表：

```java
1   // TODO inject method with no dependencies will be called
2   // TODO inject method with dependencies will be injected
3   // TODO override inject method from superclass
4   // TODO include dependencies from inject methods
5   // TODO throw exception if type parameter defined
```

## [](#无参方法注入 "无参方法注入")无参方法注入

定义一个带有无参方法注入的类

```java
1   static class InjectMethodWithNoDependencies {
2       boolean called = false; // 用于验证方法是否被调用
3   
4       @Inject
5       void install() {
6           called = true;
7       }
8   }
```

定义测试：

```java
1   // TODO: inject method with no dependencies will be called
2   @Test
3   public void should_call_inject_method_with_no_dependencies() {
4       config.bind(InjectMethodWithNoDependencies.class, InjectMethodWithNoDependencies.class);
5       InjectMethodWithNoDependencies instance = config.getContext().get(InjectMethodWithNoDependencies.class).get();
6   
7       assertTrue(instance.called);
8   }
```

实现，同理先找到并记录所有被 `@Inject` 标注的方法

![Snipaste_2024-08-13_14-51-24](~/assets/images/spring-di/Snipaste_2024-08-13_14-51-24.png)

获取实例时，调用这些方法注入依赖：

![image-20240813151931496](~/assets/images/spring-di/image-20240813151931496.png)

## [](#有参方法注入 "有参方法注入")有参方法注入

新建有参方法注入类：

```java
1   static class InjectMethodWithDependencies {
2       Dependency dependency;
3   
4       @Inject
5       void install(Dependency dependency) {
6           this.dependency = dependency;
7       }
8   }
```

构造测试

```java
1   // TODO: inject method with dependencies will be injected
2   @Test
3   public void should_call_inject_method_with_dependencies() {
4       Dependency dependency = new Dependency() {
5       };
6       config.bind(Dependency.class, dependency);
7       config.bind(InjectMethodWithDependencies.class, InjectMethodWithDependencies.class);
8       InjectMethodWithDependencies instance = config.getContext().get(InjectMethodWithDependencies.class).get();
9   
10      assertSame(dependency, instance.dependency);
11  }
```

运行测试，直接通过，说明不需要修改生产代码。

## [](#对依赖的检查 "对依赖的检查")对依赖的检查

检查依赖是否存在、是否存在循环依赖

构造测试，减小测试的粒度，直接对 ConstructorInjectionProvider 进行测试：

```java
1   // TODO: include dependencies from inject methods
2   @Test
3   public void should_include_method_dependency_in_dependencies() {
4       ConstructorInjectionProvider<InjectMethodWithDependencies> provider =
5               new ConstructorInjectionProvider<>(InjectMethodWithDependencies.class);
6   
7       assertArrayEquals(new Class<?>[]{Dependency.class}, provider.getDependencies().toArray(Class<?>[]::new));
8   }
```

同理需要在 getDependencies 方法中增加返回方法注入点所需的依赖参数。

```java
1   @Override
2   public List<Class<?>> getDependencies() {
3       Stream<? extends Class<?>> b = injectFields.stream().map(Field::getType);
4       Stream<? extends Class<?>> a = Arrays.stream(injectConstructor.getParameters()).map(Parameter::getType);
5       Stream<Class<?>> c = injectMethods.stream().flatMap(m -> Arrays.stream(m.getParameterTypes()));
6       Stream<Class<?>> concat = Stream.concat(a, b);
7       return Stream.concat(concat, c).collect(Collectors.toList());
8   }
```

> 使用 flatMap 的原因：
> 
> 由于 `getParameterTypes()` 返回的是一个 `Class<?>[]` 数组，每次调用都会返回多个元素，而不是单个元素。因此，如果你直接使用 `map` 操作来转换这些数组，你将得到一个由多个 `Class<?>[]` 组成的流，而不是一个扁平化的流，其中包含所有的 `Class<?>` 对象。
> 
> 为了解决这个问题，你需要使用 `flatMap` 操作来“展平”这些数组，将它们合并成一个单一的流，这样你就可以继续对这个流进行操作，比如收集结果到一个列表中。

## [](#父类和子类的方法注入 "父类和子类的方法注入")父类和子类的方法注入

方法注入的难点，主要是在子类和父类之间方法注入的调用关系

### [](#子类注册时，需要调用父类的注入点方法 "子类注册时，需要调用父类的注入点方法")子类注册时，需要调用父类的注入点方法

新建父子类：

```java
1   // TODO: override inject method from superclass
2   static class SuperClassWithInjectMethod {
3       boolean superCalled = false;
4       @Inject
5       void install() {
6           superCalled = true;
7       }
8   }
9   static class SubclassWithInjectMethod extends SuperClassWithInjectMethod {
10      boolean subCalled = false;
11      @Inject
12      void installAnother() {
13          subCalled = true;
14      }
15  }
```

构造测试：

```java
1   @Test
2   public void should_inject_dependencies_via_inject_method_from_superclass() {
3       config.bind(SubclassWithInjectMethod.class, SubclassWithInjectMethod.class);
4       SubclassWithInjectMethod instance = config.getContext().get(SubclassWithInjectMethod.class).get();
5   
6       assertTrue(instance.superCalled);
7       assertTrue(instance.subCalled);
8   }
```

运行测试，测试不通过，父类的注入方法不会被调用，superCalled 为 false：

```plaintext
1   Expected :true
2   Actual   :false
```

原因是，获取方法注入点时，只获取了当前类的方法：

```java
1   private List<Method> getInjectMethods(Class<T> component) {
2       return Arrays.stream(component.getDeclaredMethods())
3               .filter(m -> m.isAnnotationPresent(Inject.class))
4               .toList();
5   }
```

类似于获取父类字段注入点的逻辑，通过递归找到父类注入方法的形式获取：

```java
1   private List<Method> getInjectMethods(Class<T> component) {
2       Class<T> current = component;
3       List<Method> injectMethods = new ArrayList<>();
4       while (current != Object.class) {
5           injectMethods.addAll(Arrays.stream(current.getDeclaredMethods())
6                   .filter(m -> m.isAnnotationPresent(Inject.class))
7                   .toList());
8           current = (Class<T>) current.getSuperclass();
9       }
10      return injectMethods;
11  }
```

### [](#子类注册时，先调用父类的注入点方法 "子类注册时，先调用父类的注入点方法")子类注册时，先调用父类的注入点方法

在注册子类时，不仅要调用父类的注入点方法，而且需要让父类的注入点方法优先于子类的注入点方法调用

修改父子类的内部状态，通过数值确定调用的顺序：

```java
1   // TODO: override inject method from superclass
2   static class SuperClassWithInjectMethod {
3       int superCalled = 0;
4       @Inject
5       void install() {
6           superCalled = 1;
7       }
8   }
9   static class SubclassWithInjectMethod extends SuperClassWithInjectMethod {
10      int subCalled = 0;
11      @Inject
12      void installAnother() {
13          subCalled = superCalled + 1;
14      }
15  }
```

修改测试：

```java
1   @Test
2   public void should_inject_dependencies_via_inject_method_from_superclass() {
3       config.bind(SubclassWithInjectMethod.class, SubclassWithInjectMethod.class);
4       SubclassWithInjectMethod instance = config.getContext().get(SubclassWithInjectMethod.class).get();
5   
6       assertEquals(1, instance.superCalled);
7       assertEquals(2, instance.subCalled);
8   }
```

运行测试，测试不通过，说明子类先于父类执行注入点方法。

因为，子类的注入点方法是先于父类的注入点方法加入到方法列表的，这里最简单的实现就是将方法列表 reverse 倒序一下：

```java
1   private List<Method> getInjectMethods(Class<T> component) {
2       Class<T> current = component;
3       List<Method> injectMethods = new ArrayList<>();
4       while (current != Object.class) {
5           injectMethods.addAll(Arrays.stream(current.getDeclaredMethods())
6                   .filter(m -> m.isAnnotationPresent(Inject.class))
7                   .toList());
8           current = (Class<T>) current.getSuperclass();
9       }
10      Collections.reverse(injectMethods);
11      return injectMethods;
12  }
```

### [](#Override-注入点方法的情况 "Override 注入点方法的情况")Override 注入点方法的情况

在 `@Inject` 的描述中，关于方法的注入有如下的限制：

> A method annotated with @Inject that overrides another method annotated with @Inject will only be injected once per injection request per instance. A method with no @Inject annotation that overrides a method annotated with @Inject will not be injected.
> 
> 被 @Inject 注解的方法如果覆盖了另一个同样被 @Inject 注解的方法，则在每次实例的注入请求中只会被注入一次。没有 @Inject 注解的方法如果覆盖了一个被 @Inject 注解的方法，则不会被注入。
> 
> > 说明：这里的调用一次是指只调用子类中的方法，不会调用父类的方法。

#### [](#子类覆盖的方法被-Inject-标注 "子类覆盖的方法被 Inject 标注")子类覆盖的方法被 Inject 标注

修改测试的父类：

> 更好的方法是子类和父类设置不同的值，使用++递增的话，不能很明确的知道是应该调用哪个方法。这里应该调用的是子类中的方法。

```java
1   // TODO: override inject method from superclass
2   static class SuperClassWithInjectMethod {
3       int superCalled = 0;
4       @Inject
5       void install() {
6           superCalled++;
7       }
8   }
```

构造测试，验证父类的注入点方法被带有Inject方法覆盖时，父类的注入点方法不会被调用，只会调用一次子类的调用点方法。

```java
1   static class SubclassWithOverrideInjectMethod extends SuperClassWithInjectMethod {
2       @Inject
3       void install() {
4           super.install();
5       }
6   }
7   @Test
8   public void should_only_call_once_if_subclass_override_superclass_inject_method_with_inject() {
9       config.bind(SubclassWithOverrideInjectMethod.class, SubclassWithOverrideInjectMethod.class);
10      SubclassWithOverrideInjectMethod instance = config.getContext().get(SubclassWithOverrideInjectMethod.class).get();
11  
12      assertEquals(1, instance.superCalled);
13  }
```

实现，在获取注入点方法时，需要判断如果父类的注入点方法被覆盖，那么可以将其过滤掉，即可以不用被调用。

因为这里是先找到子类的方法，所以可以从目前找到的方法中再判断是否有和当前类（父类）同名、同签名的方法（即覆盖的方法），有则过滤掉。

![image-20240813170732077](~/assets/images/spring-di/image-20240813170732077.png)

#### [](#子类覆盖的方法未被-Inject-标注 "子类覆盖的方法未被 Inject 标注")子类覆盖的方法未被 Inject 标注

这里子类和父类的方法应该要都不会被调用

```java
1   static class SuperClassWithInjectMethod {
2       int superCalled = 0;
3       @Inject
4       void install() {
5           superCalled++;
6       }
7   }
8   static class SubclassWithOverrideInjectMethodWithoutInject extends SuperClassWithInjectMethod {
9       void install() {
10          super.install();
11      }
12  }
13  @Test
14  public void should_only_call_once_if_subclass_override_superclass_inject_method_without_inject() {
15      config.bind(SubclassWithOverrideInjectMethodWithoutInject.class, SubclassWithOverrideInjectMethodWithoutInject.class);
16      SubclassWithOverrideInjectMethodWithoutInject instance = config.getContext().get(SubclassWithOverrideInjectMethodWithoutInject.class).get();
17  
18      assertEquals(0, instance.superCalled);
19  }
```

测试不通过，所以就是有一个被 Inject 标注的方法被加入到了注入点列表中。

> 子类的方法中需要调用 super.install(); 应该是因为该方法被覆盖，调用时执行的是子类的方法。
> 
> 所以要解决这个问题，还是要避免将父类的被 Inject 标注的方法加入的注入点方法列表。

实现：

![image-20240813175302973](~/assets/images/spring-di/image-20240813175302973.png)

```java
1   private List<Method> getInjectMethods(Class<T> component) {
2       Class<T> current = component;
3       List<Method> injectMethods = new ArrayList<>();
4       while (current != Object.class) {
5           injectMethods.addAll(Arrays.stream(current.getDeclaredMethods())
6                   .filter(m -> m.isAnnotationPresent(Inject.class))
7                   .filter(m -> injectMethods.stream().noneMatch(im -> im.getName().equals(m.getName()) &&
8                           Arrays.equals(im.getParameterTypes(), m.getParameterTypes())))
9                   .filter(m -> Arrays.stream(component.getDeclaredMethods())
10                          .filter(m1 -> !m1.isAnnotationPresent(Inject.class))
11                          .noneMatch(m1 -> m1.getName().equals(m.getName()) &&
12                                  Arrays.equals(m1.getParameterTypes(), m.getParameterTypes())))
13                  .toList());
14          current = (Class<T>) current.getSuperclass();
15      }
16      Collections.reverse(injectMethods);
17      return injectMethods;
18  }
```

# [](#Sad-Path "Sad Path")Sad Path

目前，还剩下几个 sad path，完成这几个 sad path 那么注入部分就大体上完成了。

*   如果注册的组件不可实例化，则抛出异常
    
    *   抽象类
        
    *   接口
        

```java
1   // TODO: abstract class
2   // TODO: interface
```

*   字段注入
    *   如果字段为 final 则抛出异常

```java
1   // TODO: throw exception if filed is final
```

*   方法注入
    *   如果方法定义类型参数，则抛出异常

```java
1   // TODO: throw exception if type parameter defined
2   
3   /**
4   在 Inject 的注释中有一个 do not declare type parameters of their own. 的注释，即不要在方法上声明类型参数
5   */
```

> 在Java中，类型参数（Type Parameter）是泛型编程的基础概念之一。它允许你在定义类或方法时使用一种占位类型的机制，这种占位类型可以在使用这些类或方法时具体化为实际的类型。类型参数通常用于实现泛型类、接口或方法，以便它们可以处理多种数据类型而不需要为每种类型重复代码。
> 
> 类型参数通常用一个大写字母表示，如 `E`, `T`, `K` 等，但也可以使用任何有效的标识符。例如，在定义一个泛型类时，你可以这样写：
> 
> ```java
> 1   public class Box<T> {
> 2    private T item;
> 3   
> 4    public void set(T item) {
> 5        this.item = item;
> 6    }
> 7   
> 8    public T get() {
> 9        return item;
> 10   }
> 11  }
> ```
> 
> 在这个例子中，`T` 就是一个类型参数。当你创建 `Box` 类的实例时，你需要指定 `T` 的实际类型，例如：
> 
> ```java
> 1   Box<String> stringBox = new Box<>(); // T is String
> 2   Box<Integer> intBox = new Box<>();   // T is Integer
> ```
> 
> 这里，`T` 分别被具体化为 `String` 和 `Integer` 类型。
> 
> 类型参数还可以有边界限制，这意味着你可以指定一个类型参数必须是某个特定类的子类或者实现某个特定接口。例如：
> 
> ```java
> 1   public class Box<T extends Comparable<T>> {
> 2    // ...
> 3   }
> ```
> 
> 这表示 `T` 必须实现 `Comparable` 接口。这样，你就可以在类内部安全地调用 `T` 的 `compareTo` 方法。

## [](#注册抽象类 "注册抽象类")注册抽象类

创建抽象类：

> 这里使用构造器注入，其实这里不用实现 Component 也是可以的

```java
1   abstract class AbstractComponent implements Component{
2       @Inject
3       public AbstractComponent() {
4       }
5   }
```

构造测试：

```java
1   @Test
2   public void should_throw_exception_if_component_is_abstract() {
3       assertThrows(IllegalComponentException.class, () -> new ConstructorInjectionProvider<>(AbstractComponent.class));
4   }
```

实现，创建 ConstructorInjectionProvider 时校验其是否为抽象类

```java
1   public ConstructorInjectionProvider(Class<T> component) {
2       if (Modifier.isAbstract(component.getModifiers())) throw new IllegalComponentException();
3   
4       this.injectConstructor = getInjectConstructor(component);
5       this.injectFields = getInjectFields(component);
6       this.injectMethods = getInjectMethods(component);
7   }
```

## [](#注册接口 "注册接口")注册接口

不需要创建新类，直接可以注册 Component 接口

构造测试：

```java
1   // TODO: interface
2   @Test
3   public void should_throw_exception_if_component_is_interface() {
4       assertThrows(IllegalComponentException.class, () -> new ConstructorInjectionProvider<>(Component.class));
5   }
```

运行测试，直接通过，因为接口的 Modifier 本身就是抽象的。

## [](#字段注入时，字段为-final-时 "字段注入时，字段为 final 时")字段注入时，字段为 final 时

新建测试类：

```java
1   static class FinalInjectField {
2       @Inject
3       final Dependency dependency = null;
4   }
```

新建测试：

```java
1   @Test
2   public void should_throw_exception_if_field_is_final() {
3       assertThrows(IllegalComponentException.class, () -> new ConstructorInjectionProvider<>(FinalInjectField.class));
4   }
```

实现：

> 可以在 getInjectFields 中检查并抛出异常，也可以在 ConstructorInjectionProvider 构造函数中检查并抛出异常，这里是在构造函数中检查。

```java
1   public ConstructorInjectionProvider(Class<T> component) {
2           if (Modifier.isAbstract(component.getModifiers())) throw new IllegalComponentException();
3   
4           this.injectConstructor = getInjectConstructor(component);
5           this.injectFields = getInjectFields(component);
6           this.injectMethods = getInjectMethods(component);
7   
8           if (injectFields.stream().anyMatch(f -> Modifier.isFinal(f.getModifiers()))) throw new IllegalComponentException();
9       }
```

## [](#方法定义类型参数 "方法定义类型参数")方法定义类型参数

新建类

```java
1   static class InjectMethodWithTypeParameter {
2       @Inject
3       <T> void install() {
4       }
5   }
```

构造测试：

```java
1   @Test
2   public void should_throw_exception_if_method_has_type_parameter() {
3       assertThrows(IllegalComponentException.class, () -> new ConstructorInjectionProvider<>(InjectMethodWithTypeParameter.class));
4   }
```

实现：

![image-20240814102238573](~/assets/images/spring-di/image-20240814102238573.png)

# [](#重构测试代码 "重构测试代码")重构测试代码

目前，我们的测试是按照构造器注入、字段注入、方法注入的方式组织的。但是我们的生产代码的架构是有调整的。

这就造成了生产代码和测试之间存在一些不一致的情况。

也造成了随着TDD的进行，我们前后实现类似功能的测试会因为重构导致的生产代码的变化而变化，比如，在构造器注入中我们对依赖的检查是完整的端到端的功能测试，而经过重构后，我们后面的字段注入和方法注入都是更细粒度的测试。

> 我们通过TDD的测试，可以还原整个开发流程，但是从结果上看，这并不意味着我们得到了最好的一整套测试用例。
> 
> 所以我们就需要使用重构的方式，对我们的测试代码进行重构，以得到更好的组织形式的测试。
> 
> 这才能保证，我们在TDD之后我们能得到结构优秀的代码，同时在测试中真实反映代码的意图，而不仅仅是单纯的展现我们实现功能的过程。

> 代码不仅仅是资产，也是负债。需要持续不断的维护。

## [](#删除不必要的测试 "删除不必要的测试")删除不必要的测试

```java
1   // dependencies not exist
2   @Test
3   public void should_throw_exception_if_dependency_not_found() {
4       config.bind(Component.class, ComponentWithInjectConstructor.class);
5   
6       DependencyNotFoundException exception = assertThrows(DependencyNotFoundException.class, () -> {
7           config.getContext();
8       });
9   
10      assertEquals(Dependency.class, exception.getDependency());
11      assertEquals(Component.class, exception.getComponent());
12  }
13  @Test
14  public void should_throw_exception_if_transitive_dependency_not_found() {
15      config.bind(Component.class, ComponentWithInjectConstructor.class);
16      config.bind(Dependency.class, DependencyWithInjectConstructor.class); // 缺失 String 类型的依赖
17  
18      DependencyNotFoundException exception = assertThrows(DependencyNotFoundException.class, () -> {
19          config.getContext();
20      });
21  
22      assertEquals(String.class, exception.getDependency());
23      assertEquals(Dependency.class, exception.getComponent());
24  }
```

对于这两个依赖不存在的测试，后一个测试是没有必要的，因为在我们的生产代码进行重构后，对依赖的检查不在要求？？？？？

## [](#移动部分测试到新的测试上下文 "移动部分测试到新的测试上下文")移动部分测试到新的测试上下文

对于一下三个对依赖进行检查的测试，目前在 ConstructorInjection 上下文中

```java
1   // dependencies not exist
2   @Test
3   public void should_throw_exception_if_dependency_not_found() {
4       config.bind(Component.class, ComponentWithInjectConstructor.class);
5   
6       DependencyNotFoundException exception = assertThrows(DependencyNotFoundException.class, () -> {
7           config.getContext();
8       });
9   
10      assertEquals(Dependency.class, exception.getDependency());
11      assertEquals(Component.class, exception.getComponent());
12  }
13  
14  
15  // cyclic dependencies
16  @Test // A -> B -> A
17  public void should_throw_exception_if_cyclic_dependencies() {
18      config.bind(Component.class, ComponentWithInjectConstructor.class);
19      config.bind(Dependency.class, DependencyDependedOnComponent.class);
20  
21      CyclicDependenciesException exception =
22              assertThrows(CyclicDependenciesException.class, () -> config.getContext());
23  
24      Set<Class<?>> classes = Sets.newSet(exception.getComponents());
25  
26      assertEquals(2, classes.size());
27      assertTrue(classes.contains(Component.class));
28      assertTrue(classes.contains(Dependency.class));
29  }
30  @Test // A -> B -> C -> A
31  public void should_throw_exception_if_transitive_cyclic_dependencies() {
32      config.bind(Component.class, ComponentWithInjectConstructor.class);
33      config.bind(Dependency.class, DependencyDependedOnAnotherDependency.class);
34      config.bind(AnotherDependency.class, AnotherDependencyDependedOnComponent.class);
35  
36      CyclicDependenciesException exception =
37              assertThrows(CyclicDependenciesException.class, () -> config.getContext());
38  
39      List<Class<?>> components = Arrays.stream(exception.getComponents()).toList();
40  
41      assertEquals(3, components.size());
42      assertTrue(components.contains(Component.class));
43      assertTrue(components.contains(Dependency.class));
44      assertTrue(components.contains(AnotherDependency.class));
45  }
```

可以将这三个测试移动到一个新的上下文中，这个上下文要体现出我们的意图，这里我们定义一个名为 DependencyCheck 的测试上下文。

```java
1   @Nested
2   public class DependencyCheck {
3   
4   }
```

将前文提到的三个测试移动到这个上下文中

```java
1   @Nested
2   public class DependencyCheck {
3   
4       // dependencies not exist
5       @Test
6       public void should_throw_exception_if_dependency_not_found() {
7           config.bind(Component.class, ComponentWithInjectConstructor.class);
8   
9           DependencyNotFoundException exception = assertThrows(DependencyNotFoundException.class, () -> {
10              config.getContext();
11          });
12  
13          assertEquals(Dependency.class, exception.getDependency());
14          assertEquals(Component.class, exception.getComponent());
15      }
16  
17  
18      // cyclic dependencies
19      @Test // A -> B -> A
20      public void should_throw_exception_if_cyclic_dependencies() {
21          config.bind(Component.class, ComponentWithInjectConstructor.class);
22          config.bind(Dependency.class, DependencyDependedOnComponent.class);
23  
24          CyclicDependenciesException exception =
25                  assertThrows(CyclicDependenciesException.class, () -> config.getContext());
26  
27          Set<Class<?>> classes = Sets.newSet(exception.getComponents());
28  
29          assertEquals(2, classes.size());
30          assertTrue(classes.contains(Component.class));
31          assertTrue(classes.contains(Dependency.class));
32      }
33      @Test // A -> B -> C -> A
34      public void should_throw_exception_if_transitive_cyclic_dependencies() {
35          config.bind(Component.class, ComponentWithInjectConstructor.class);
36          config.bind(Dependency.class, DependencyDependedOnAnotherDependency.class);
37          config.bind(AnotherDependency.class, AnotherDependencyDependedOnComponent.class);
38  
39          CyclicDependenciesException exception =
40                  assertThrows(CyclicDependenciesException.class, () -> config.getContext());
41  
42          List<Class<?>> components = Arrays.stream(exception.getComponents()).toList();
43  
44          assertEquals(3, components.size());
45          assertTrue(components.contains(Component.class));
46          assertTrue(components.contains(Dependency.class));
47          assertTrue(components.contains(AnotherDependency.class));
48      }
49  
50  }
```

## [](#重构-ConstructorInjection-上下文 "重构 ConstructorInjection 上下文")重构 ConstructorInjection 上下文

以下的这两个方法，与当前的架构不一致，

![image-20240814114238683](~/assets/images/spring-di/image-20240814114238683.png)

抽取出 getBind 方法，修改这两个方法的实现

```java
1   // sad path
2   // multi inject constructors
3   @Test
4   public void should_throw_exception_if_multi_inject_constructors_provided() {
5       assertThrows(IllegalComponentException.class, () -> {
6           getBind(ComponentWithMultiInjectConstructors.class);
7       });
8   }
9   
10  private void getBind(Class<? extends Component> implementation) {
11      config.bind(Component.class, implementation);
12  }
13  
14  // no default constructor and inject constructor
15  @Test
16  public void should_throw_exception_if_no_inject_constructor_nor_default_constructor_provided() {
17      assertThrows(IllegalComponentException.class, () -> {
18          getBind(ComponentWithNoInjectConstructorNorDefaultConstructor.class);
19      });
20  }
```

将 getBind的实现修改为：

```java
1   private void getBind(Class<? extends Component> implementation) {
2       new ConstructorInjectionProvider<>(implementation);
3   }
```

inline getBind 方法

> inline 后需要稍微调整一下，比如移除不必要的型转

```java
1   // sad path
2   // multi inject constructors
3   @Test
4   public void should_throw_exception_if_multi_inject_constructors_provided() {
5       assertThrows(IllegalComponentException.class, () -> new ConstructorInjectionProvider<>(ComponentWithMultiInjectConstructors.class));
6   }
7   
8   // no default constructor and inject constructor
9   @Test
10  public void should_throw_exception_if_no_inject_constructor_nor_default_constructor_provided() {
11      assertThrows(IllegalComponentException.class, () -> new ConstructorInjectionProvider<>(ComponentWithNoInjectConstructorNorDefaultConstructor.class));
12  }
```

修改之后，这几个测试就有了一样的结构：

![image-20240814115236417](~/assets/images/spring-di/image-20240814115236417.png)

## [](#在-ConstructorInjection-中增加对依赖校验的测试 "在 ConstructorInjection 中增加对依赖校验的测试")在 ConstructorInjection 中增加对依赖校验的测试

增加这个测试为了统一与FieldInjection、MethodInjection测试上下文的测试组织形式，使得这几个测试上下文都保持一个一致的结构。

```java
1   @Test
2   public void should_include_dependency_from_inject_constructor() {
3       ConstructorInjectionProvider<ComponentWithInjectConstructor> provider =
4               new ConstructorInjectionProvider<>(ComponentWithInjectConstructor.class);
5   
6       assertArrayEquals(new Class<?>[]{Dependency.class}, provider.getDependencies().toArray(Class<?>[]::new));
7   }
```

## [](#创建-InjectionTest-并移出-ContainerTest "创建 InjectionTest 并移出 ContainerTest")创建 InjectionTest 并移出 ContainerTest

将关于注入的三个测试上下文，放入一个 InjectionTest 上下文中，用于后续将其移出 ContainerTest，以形成一个独立的测试类，减少ContainerTest 类中的代码数量，便于理解。

![Snipaste_2024-08-14_12-03-14](~/assets/images/spring-di/Snipaste_2024-08-14_12-03-14.png)

因为当前上下文中，大量依赖 config，所以也需要将 setUp的代码移入 InjectionTest

![](~/assets/images/spring-di/Snipaste_2024-08-14_13-43-13.png)

接着需要将 InjectionTest 移出 ContainerTest，这里对 InjectionTest 执行两次 Move Inner Class to Upper Level 重构，就可以将其从 ContainerTest 中移出：

![image-20240814134740365](~/assets/images/spring-di/image-20240814134740365.png)

最终移出到测试目录的最顶层：

![image-20240814135151138](~/assets/images/spring-di/image-20240814135151138.png)

# [](#重构-InjectionTest "重构 InjectionTest")重构 InjectionTest

目前在 InjectionTest 的测试上下文中，存在不同的测试粒度

![image-20240814135657701](~/assets/images/spring-di/image-20240814135657701.png)

在同一个测试上下文中，我们最好希望它们的测试粒度是一样的。

这里，我们就希望将对 config 粒度的功能测试，都能重构为对 ConstructorInjectionProvider 粒度的单元测试。

观察：

![image-20240814151410275](~/assets/images/spring-di/image-20240814151410275.png)

对于 config 的测试都需要执行 `config.bind(XXX)` + `config.getContext().get(XXX).get()` 方法来获取一个组件，所以这里重构方向就是将 `config.getContext().get(XXX).get()` 方法，修改为通过创建 `ConstructorInjectionProvider` 的方式来获取一个组件。

先将 `config.bind(XXX)` + `config.getContext().get(XXX).get()` 提取为一个通用的方法。

第一步，因为需要支持很多类型，这里先提取参数：

![Snipaste_2024-08-14_15-26-55](~/assets/images/spring-di/Snipaste_2024-08-14_15-26-55.png)

再提取方法：

![Snipaste_2024-08-14_15-28-06](~/assets/images/spring-di/Snipaste_2024-08-14_15-28-06.png)

```java
1   private Component getComponent(Class<Component> type, Class<ComponentWithDefaultConstructor> implementation) {
2       config.bind(type, implementation);
3       Component instance = config.getContext().get(type).get();
4       return instance;
5   }
```

提取的方法的签名无法支持我们其他代码的类型，需要做一些范型调整：

```java
1   private <T, I extends T> T getComponent(Class<T> type, Class<I> implementation) {
2       config.bind(type, implementation);
3       T instance = config.getContext().get(type).get();
4       return instance;
5   }
```

将提取的参数先 inline 回去：

![image-20240814153437033](~/assets/images/spring-di/image-20240814153437033.png)

inline 后，这段代码就会变成如下形式：

![image-20240814153602000](~/assets/images/spring-di/image-20240814153602000.png)

观察其他测试代码，可以发现，有很多相似的代码，可以改为调用上一步提取出的 getComponent，比如：

![image-20240814153744147](~/assets/images/spring-di/image-20240814153744147.png)

![image-20240814153851651](~/assets/images/spring-di/image-20240814153851651.png)

接下来就是，逐步将这些代码替换为调用 getComponent 来获取组件。

替换完成后，我们还会发现，这些测试代码中很多都使用了一个 Dependency 实例：

![Snipaste_2024-08-14_15-59-28](~/assets/images/spring-di/Snipaste_2024-08-14_15-59-28.png)

可以将这个放到 setUp 中去：

![image-20240814160224365](~/assets/images/spring-di/image-20240814160224365.png)

接着就可以逐个移除掉测试用例中的创建并bind dependecy 的代码。

接着，替换掉 getComponent中的实现，就可以通过 ConstructorInjectionProvider 返回一个实例，如下所示，只要 执行 provider.get 方法就可以返回实例，但是这里的问题是，该方法需要一个 context 容器作为参数：

![Snipaste_2024-08-14_16-12-35](~/assets/images/spring-di/Snipaste_2024-08-14_16-12-35.png)

可以通过测试替身的方式创建 context 容器，并且我们知道，provider 使用这个 context 是用来从容器中获取 provider 需要的依赖的，也就是 provider 需要调用 context 的 get 方法。并且当前 provider 需要的依赖类型就是 Dependency。

所以 setUp 可以是实现为：

![image-20240814162037571](~/assets/images/spring-di/image-20240814162037571-1723623638469-6.png)

并把 getComponent 方法的实现修改为：

```java
1   private <T, I extends T> T getComponent(Class<T> type, Class<I> implementation) {
2       ConstructorInjectionProvider<I> provider = new ConstructorInjectionProvider<>(implementation);
3       return provider.get(context);
4   }
```

同样的，也可为 Dependency 创建测试替身：

![image-20240814162619203](~/assets/images/spring-di/image-20240814162619203.png)

如果下面的测试抛异常的话，需要修改一下测试替身的返回数据：

![image-20240814163326742](~/assets/images/spring-di/image-20240814163326742.png)

接着，将 getComponent 方法 inline 一下：

![image-20240814163812035](~/assets/images/spring-di/image-20240814163812035.png)

至此，原来使用 config 获取实例的方法，都变成了使用 ConstructorInjectionProvider 来获取实例。也就是说我们绝大多数的测试的粒度都调整到了 ConstructorInjectionProvider 之上。

现在，只剩下一个地方在使用 config ：

![image-20240814164435758](~/assets/images/spring-di/image-20240814164435758.png)

稍微调整一下这个测试，我们会发现，把 config 删掉也不会有什么影响：

![image-20240814165056094](~/assets/images/spring-di/image-20240814165056094.png)

同样的，现在 setUp 中的 config 也没什么用了：

![image-20240814165358387](~/assets/images/spring-di/image-20240814165358387.png)

删掉 config 后，测试依然通过。就此，config 就与我们的测试上下文彻底无关了。

> 另外呢，还可以将在 ContainerTest 中定义的类也移动到 InjectionTest中，或在 InjectionTest 中重新定义并使用在这个测试上下文中使用的类。
> 
> 比如说 ComponentWithDefaultConstructor 只在 InjectionTest 中被使用，但是却是在 ContainerTest 定义，好的做法是将其移动到 InjectionTest 中，但是这里最好还是重新定义一个新的类（不必实现任何接口），因为这个 ComponentWithDefaultConstructor 还实现了 Component 接口。这个需要自己去实现。

> 另外，以下的这两个测试其实功能是一样的，下面的测试可以删掉
> 
> ![image-20240814170235565](~/assets/images/spring-di/image-20240814170235565.png)

# [](#测试文档化 "测试文档化")测试文档化

我们说测试应该是文档，但是文档不应该是我们实现的过程，因为在TDD中测试就是实现过程中的里程碑。

> 对于TDD来说，测试天然并不是文档，测试是实现过程中的里程碑（或记录）。需要将测试变为文档是需要经过很多努力的。
> 
> 只有在这个过程中间我们将我们需要知识和需要表达的内容进行足够的提取和刻意地组织，才能使测试变成一个文档。

> 因为TDD的测试主要是一种里程碑，帮助我们驱动开发的，它并不是真的站在软件测试的角度上去写的。
> 
> > 开发人员所写的测试，和测试人员所希望看到的测试的类型其实是不同的。测试人员更多的是关注测试的完备性、对条件的覆盖。这两种测试之间是存在鸿沟的，需要刻意的调整和梳理。
> 
> 一旦我们把TDD测试的功能写完，其实我们可以通过扩展（不能讲是重构了），把它 Convert 成一个更接近于测试需要的测试。
> 
> 因为这个时候测试的骨架已经形成，我们只需要把它变成参数化或是数据驱动的方式去做，使测试可以覆盖更大范围的场景。

对测试进行分类分组、保持一致的命名，使其更加文档化。

## [](#文档化-InjectionTest "文档化 InjectionTest")文档化 InjectionTest

### [](#统一命名 "统一命名")统一命名

统一测试命名，使其更加文档化：

```plaintext
1   should_bind_type_to_a_class_with_default_constructor
```

修改为

```plaintext
1   should_call_default_constructor_if_no_inject_constructor
```

> 因为 bind 是针对 config 描述的测试

再一个：

```plaintext
1   should_bind_type_to_a_class_with_inject_constructor
```

修改为：

```plaintext
1   should_inject_dependency_via_inject_constructor
```

### [](#细化分组 "细化分组")细化分组

将 ConstructorInjection、FieldInjection、MethodInjection 分别再按 Injection 和 IllegalInjectXXX 进行分组。

> 具体的结果，请查看 commit id 为 a9590a2a 的 commit 记录。

![image-20240814175622797](~/assets/images/spring-di/image-20240814175622797.png)

当然，视情况，还可以进行更细一步的分组。

## [](#文档化-ContainerTest "文档化 ContainerTest")文档化 ContainerTest

目前 ContainerTest 中还剩下的测试有：

```java
1   ContextConfig config;
2   
3   @BeforeEach
4   public void setUp(){
5       config = new ContextConfig();
6   }
7   
8   // 组件构造相 关的测试类
9   @Nested
10  public class ComponentConstruction{
11  
12      // instance
13      @Test
14      public void should_bind_type_to_a_specific_instance() {
15          // 创建一个实现了 Component 接口的匿名内部类实例
16          Component instance = new Component() {
17          };
18          config.bind(Component.class, instance);
19  
20          assertSame(instance, config.getContext().get(Component.class).get());
21      }
22  
23      // component does not exist
24      @Test
25      public void should_return_empty_if_component_not_defined() {
26          Optional<Component> component = config.getContext().get(Component.class);
27          assertTrue(component.isEmpty());
28      }
29  
30      @Nested
31      public class DependencyCheck {
32  
33          // dependencies not exist
34          @Test
35          public void should_throw_exception_if_dependency_not_found() {
36              config.bind(Component.class, ComponentWithInjectConstructor.class);
37  
38              DependencyNotFoundException exception = assertThrows(DependencyNotFoundException.class, () -> {
39                  config.getContext();
40              });
41  
42              assertEquals(Dependency.class, exception.getDependency());
43              assertEquals(Component.class, exception.getComponent());
44          }
45  
46  
47          // cyclic dependencies
48          @Test // A -> B -> A
49          public void should_throw_exception_if_cyclic_dependencies() {
50              config.bind(Component.class, ComponentWithInjectConstructor.class);
51              config.bind(Dependency.class, DependencyDependedOnComponent.class);
52  
53              CyclicDependenciesException exception =
54                      assertThrows(CyclicDependenciesException.class, () -> config.getContext());
55  
56              Set<Class<?>> classes = Sets.newSet(exception.getComponents());
57  
58              assertEquals(2, classes.size());
59              assertTrue(classes.contains(Component.class));
60              assertTrue(classes.contains(Dependency.class));
61          }
62          @Test // A -> B -> C -> A
63          public void should_throw_exception_if_transitive_cyclic_dependencies() {
64              config.bind(Component.class, ComponentWithInjectConstructor.class);
65              config.bind(Dependency.class, DependencyDependedOnAnotherDependency.class);
66              config.bind(AnotherDependency.class, AnotherDependencyDependedOnComponent.class);
67  
68              CyclicDependenciesException exception =
69                      assertThrows(CyclicDependenciesException.class, () -> config.getContext());
70  
71              List<Class<?>> components = Arrays.stream(exception.getComponents()).toList();
72  
73              assertEquals(3, components.size());
74              assertTrue(components.contains(Component.class));
75              assertTrue(components.contains(Dependency.class));
76              assertTrue(components.contains(AnotherDependency.class));
77          }
78  
79      }
80  
81  }
```

这些测试都是在 Context 上下文之上的测试，我们也可以将这些测试移动到一个独立的测试类中，比如 ContextTest 中。

参考 DependencyCheck 的测试分组，这里也可以将前两个测试归类到一个名为 TypeBinding 的分类中：

![image-20240815115724375](~/assets/images/spring-di/image-20240815115724375.png)

将

```java
1   should_return_empty_if_component_not_defined
```

改名为：

```java
1   should_retrieve_empty_for_unbind_type
```

### [](#TypeBinding-注入方式参数化 "TypeBinding 注入方式参数化")TypeBinding 注入方式参数化

在 TypeBinding 分类中增加一个测试，并且使用参数化，将一个测试泛化为多个测试，分别测试根据：构造器注入、字段注入和方法注入的情况：

```java
1   // 将一个测试泛化为多个测试，分别测试根据：构造器注入、字段注入和方法注入的情况
2   @ParameterizedTest(name = "supporting {0}")
3   @MethodSource
4   public void should_bind_type_to_an_injectable_component(Class<? extends Component> componentType) {
5       Dependency dependency = new Dependency() {
6       };
7       config.bind(Dependency.class, dependency);
8       config.bind(Component.class, componentType); // 参数化测试不同的注入方式
9   
10      Optional<Component> component = config.getContext().get(Component.class);
11  
12      assertTrue(component.isPresent());
13      assertSame(dependency, component.get().dependency());
14  }
15  
16  public static Stream<Arguments> should_bind_type_to_an_injectable_component() {
17      return Stream.of(
18              Arguments.of(Named.of("Constructor Injection", TypeBinding.ConstructorInjection.class)),
19              Arguments.of(Named.of("Field Injection", TypeBinding.FieldInjection.class)),
20              Arguments.of(Named.of("Method Injection", TypeBinding.MethodInjection.class))
21      );
22  }
23  
24  
25  static class ConstructorInjection implements Component {
26      private Dependency dependency;
27  
28      @Inject
29      public ConstructorInjection(Dependency dependency) {
30          this.dependency = dependency;
31      }
32  
33      @Override
34      public Dependency dependency() {
35          return dependency;
36      }
37  }
38  
39  static class FieldInjection implements Component {
40      @Inject
41      Dependency dependency; // 目前不支持注入私有字段
42  
43      @Override
44      public Dependency dependency() {
45          return dependency;
46      }
47  }
48  
49  static class MethodInjection implements Component {
50      private Dependency dependency;
51  
52      @Inject
53      public void install(Dependency dependency) {
54          this.dependency = dependency;
55      }
56  
57      @Override
58      public Dependency dependency() {
59          return dependency;
60      }
61  }
```

注意，需要修改一下 Component 的定义，增加默认方法：

```java
1   interface Component{
2       default Dependency dependency() {return null;}
3   }
```

### [](#DependencyCheck-参数化 "DependencyCheck 参数化")DependencyCheck 参数化

同理将 DependencyCheck 中的三个测试分别参数化。

#### [](#依赖缺失 "依赖缺失")依赖缺失

测试三种不同的注入方式是否满足依赖缺失的情况：

```java
1   // dependencies not exist
2   @ParameterizedTest
3   @MethodSource
4   public void should_throw_exception_if_dependency_not_found(Class<? extends Component> componentType) {
5       config.bind(Component.class, componentType);
6   
7       DependencyNotFoundException exception = assertThrows(DependencyNotFoundException.class, () -> {
8           config.getContext();
9       });
10  
11      assertEquals(Dependency.class, exception.getDependency());
12      assertEquals(Component.class, exception.getComponent());
13  }
14  
15  public static Stream<Arguments> should_throw_exception_if_dependency_not_found() {
16      return Stream.of(
17              Arguments.of(Named.of("Constructor Injection", DependencyCheck.MissingDependencyConstructor.class)),
18              Arguments.of(Named.of("Field Injection", DependencyCheck.MissingDependencyField.class)),
19              Arguments.of(Named.of("Method Injection", DependencyCheck.MissingDependencyMethod.class))
20      );
21  }
22  
23  static class MissingDependencyConstructor implements Component{
24      @Inject
25      public MissingDependencyConstructor(Dependency dependency) {
26      }
27  }
28  
29  static class MissingDependencyField implements Component {
30      @Inject
31      Dependency dependency;
32  }
33  
34  static class MissingDependencyMethod implements Component {
35      @Inject
36      public void install(Dependency dependency) {
37      }
38  }
```

![image-20240815135153837](~/assets/images/spring-di/image-20240815135153837.png)

#### [](#直接循环依赖-1 "直接循环依赖")直接循环依赖

测试不同的注入方式的组合是否满足循环依赖的情况：

```java
1   // cyclic dependencies
2   // A -> B -> A
3   @ParameterizedTest(name = "cyclic dependency between {0} and {1}")
4   @MethodSource
5   public void should_throw_exception_if_cyclic_dependencies(Class<? extends Component> componentType,
6                                                             Class<? extends Dependency> dependencyType) {
7       config.bind(Component.class, componentType);
8       config.bind(Dependency.class, dependencyType);
9   
10      CyclicDependenciesException exception =
11              assertThrows(CyclicDependenciesException.class, () -> config.getContext());
12  
13      Set<Class<?>> classes = Sets.newSet(exception.getComponents());
14  
15      assertEquals(2, classes.size());
16      assertTrue(classes.contains(Component.class));
17      assertTrue(classes.contains(Dependency.class));
18  }
19  
20  public static Stream<Arguments> should_throw_exception_if_cyclic_dependencies() {
21      List<Arguments> arguments = new ArrayList<>();
22      for (Named component : List.of(Named.of("Constructor Injection", DependencyCheck.CyclicComponentInjectConstructor.class),
23              Named.of("Field Injection", DependencyCheck.CyclicComponentInjectField.class),
24              Named.of("Method Injection", DependencyCheck.CyclicComponentInjectMethod.class))) {
25          for (Named dependency : List.of(Named.of("Constructor Injection", DependencyCheck.CyclicDependencyInjectConstructor.class),
26                  Named.of("Field Injection", DependencyCheck.CyclicDependencyInjectField.class),
27                  Named.of("Method Injection", DependencyCheck.CyclicDependencyInjectMethod.class))) {
28              arguments.add(Arguments.of(component, dependency));
29          }
30      }
31      return arguments.stream();
32  }
33  
34  static class CyclicComponentInjectConstructor implements Component {
35      @Inject
36      public CyclicComponentInjectConstructor(Dependency dependency) {
37      }
38  }
39  
40  static class CyclicComponentInjectField implements Component {
41      @Inject
42      Dependency dependency;
43  }
44  
45  static class CyclicComponentInjectMethod implements Component {
46      @Inject
47      public void install(Dependency dependency) {
48      }
49  }
50  
51  static class CyclicDependencyInjectConstructor implements Dependency {
52      @Inject
53      public CyclicDependencyInjectConstructor(Component component) {
54      }
55  }
56  
57  static class CyclicDependencyInjectField implements Dependency {
58      @Inject
59      Component component;
60  }
61  
62  static class CyclicDependencyInjectMethod implements Dependency {
63      @Inject
64      public void install(Component component) {
65      }
66  }
```

![image-20240815135326871](~/assets/images/spring-di/image-20240815135326871.png)

#### [](#间接循环依赖 "间接循环依赖")间接循环依赖

测试不同的注入方式的组合是否能满足间接循环依赖的情况：

```java
1   // A -> B -> C -> A
2   @ParameterizedTest(name = "transitive cyclic dependency between {0}, {1} and {2}")
3   @MethodSource
4   public void should_throw_exception_if_transitive_cyclic_dependencies(Class<? extends Component> componentType,
5                                                                       Class<? extends Dependency> dependencyType,
6                                                                       Class<? extends AnotherDependency> anotherDependencyType) {
7       config.bind(Component.class, componentType);
8       config.bind(Dependency.class, dependencyType);
9       config.bind(AnotherDependency.class, anotherDependencyType);
10  
11      CyclicDependenciesException exception =
12              assertThrows(CyclicDependenciesException.class, () -> config.getContext());
13  
14      List<Class<?>> components = Arrays.stream(exception.getComponents()).toList();
15  
16      assertEquals(3, components.size());
17      assertTrue(components.contains(Component.class));
18      assertTrue(components.contains(Dependency.class));
19      assertTrue(components.contains(AnotherDependency.class));
20  }
21  
22  public static Stream<Arguments> should_throw_exception_if_transitive_cyclic_dependencies() {
23      List<Arguments> arguments = new ArrayList<>();
24      for (Named component : List.of(Named.of("Constructor Injection", DependencyCheck.CyclicComponentInjectConstructor.class),
25              Named.of("Field Injection", DependencyCheck.CyclicComponentInjectField.class),
26              Named.of("Method Injection", DependencyCheck.CyclicComponentInjectMethod.class))) {
27          for (Named dependency : List.of(Named.of("Constructor Injection", DependencyCheck.CyclicDependencyInjectConstructorWithAnotherDependency.class),
28                  Named.of("Field Injection", DependencyCheck.CyclicDependencyInjectFieldWithAnotherDependency.class),
29                  Named.of("Method Injection", DependencyCheck.CyclicDependencyInjectMethodWithAnotherDependency.class))) {
30              for (Named anotherDependency : List.of(Named.of("Constructor Injection", DependencyCheck.CyclicDependencyInjectConstructorWithComponent.class),
31                      Named.of("Field Injection", DependencyCheck.CyclicDependencyInjectFieldWithComponent.class),
32                      Named.of("Method Injection", DependencyCheck.CyclicDependencyInjectMethodWithComponent.class))) {
33                  arguments.add(Arguments.of(component, dependency, anotherDependency));
34              }
35          }
36      }
37      return arguments.stream();
38  }
39  
40  static class CyclicDependencyInjectConstructorWithAnotherDependency implements Dependency {
41      @Inject
42      public CyclicDependencyInjectConstructorWithAnotherDependency(AnotherDependency anotherDependency) {
43      }
44  }
45  
46  static class CyclicDependencyInjectFieldWithAnotherDependency implements Dependency {
47      @Inject
48      AnotherDependency anotherDependency;
49  }
50  
51  static class CyclicDependencyInjectMethodWithAnotherDependency implements Dependency {
52      @Inject
53      public void install(AnotherDependency anotherDependency) {
54      }
55  }
56  
57  static class CyclicDependencyInjectConstructorWithComponent implements AnotherDependency {
58      @Inject
59      public CyclicDependencyInjectConstructorWithComponent(Component component) {
60      }
61  }
62  
63  static class CyclicDependencyInjectFieldWithComponent implements AnotherDependency {
64      @Inject
65      Component component;
66  }
67  
68  static class CyclicDependencyInjectMethodWithComponent implements AnotherDependency {
69      @Inject
70      public void install(Component component) {
71      }
72  }
```

![image-20240815135441506](~/assets/images/spring-di/image-20240815135441506.png)

## [](#移动-ContainerTest-中的部分测试用例类 "移动 ContainerTest 中的部分测试用例类")移动 ContainerTest 中的部分测试用例类

ContainerTest 中的部分测试用例类现在只会在 InjectionTest 中使用，应该使用 Move Class 方法重构，将这些类移动到 InjectionTest 中。

![image-20240815140852626](~/assets/images/spring-di/image-20240815140852626.png)

整理好之后，测试目录的代码结构如下所示：

![image-20240815141206661](~/assets/images/spring-di/image-20240815141206661.png)

## [](#总结-1 "总结")总结

这里的 ContextTest 中的测试更接近于 API，所以也适合参数化进而更加文档化。

> 对于TDD来说，测试天然并不是文档，测试是实现过程中的里程碑（或记录）。需要将测试变为文档是需要经过很多努力的。
> 
> 只有在这个过程中间我们将我们需要知识和需要表达的内容进行足够的提取和刻意地组织，才能使测试变成一个文档。

> 因为TDD的测试主要是一种里程碑，帮助我们驱动开发的，它并不是真的站在软件测试的角度上去写的。
> 
> > 开发人员所写的测试，和测试人员所希望看到的测试的类型其实是不同的。测试人员更多的是关注测试的完备性、对条件的覆盖。这两种测试之间是存在鸿沟的，需要刻意的调整和梳理。
> 
> 一旦我们把TDD测试的功能写完，其实我们可以通过扩展（不能讲是重构了），把它 Convert 成一个更接近于测试需要的测试。
> 
> 因为这个时候测试的骨架已经形成，我们只需要把它变成参数化或是数据驱动的方式去做，就可以使测试覆盖更大范围的场景。

# [](#重构生产代码 "重构生产代码")重构生产代码

目前，我们的生产代码主要集中在 ContextConfig 和 ConstructorInjectionProvider 中。

## [](#重构-ContextConfig "重构 ContextConfig")重构 ContextConfig

这两个类里面的功能不多，如果非要重构的话

```java
1   interface ComponentProvider<T> {
2       T get(Context context);
3   
4       List<Class<?>> getDependencies();
5   }
```

改写为：

```java
1   interface ComponentProvider<T> {
2       T get(Context context);
3   
4       default List<Class<?>> getDependencies() {
5           return List.of();
6       }
7   }
```

将其改为一个函数式的接口，即将 getDependencies 方法定义为接口的默认方法。

那么就可以将下面的代码改写为使用lambda：

![image-20240814190544963](~/assets/images/spring-di/image-20240814190544963.png)

![image-20240814190717435](~/assets/images/spring-di/image-20240814190717435.png)

## [](#重构-ConstructorInjectionProvider "重构 ConstructorInjectionProvider")重构 ConstructorInjectionProvider

首先，重命名 ConstructorInjectionProvider 的名字，因为现在不仅仅是关于构造器的注入，而是所有的 Injection 都在里面。

重命名为 InjectionProvider

其他问题就是易读性比较差，并且还有一些重复。

很多地方都需要判断是否被 `Inject`注解标记，这里有比较多的重复代码：

![image-20240814193426209](~/assets/images/spring-di/image-20240814193426209.png)

先提取方法：

![image-20240814193907824](~/assets/images/spring-di/image-20240814193907824.png)

因为不止是用在 Field，还需要支持构造函数、方法注入等场景的判断，就需要将这个方法修改为支持范型的方法。

因为 isAnnotationPresent 方法是在一个接口（公共的基类）上定义的：

![image-20240814194214679](~/assets/images/spring-di/image-20240814194214679.png)

这里就可以把这个范型转换为 AnnotatedElement，那么这个方法的定义就是：

```java
1   private static <T extends AnnotatedElement> Stream<T> injectable(T[] declaredFields) {
2       return Arrays.stream(declaredFields)
3               .filter(f -> f.isAnnotationPresent(Inject.class));
4   }
```

接着，使用这个函数替换掉判断被Inject标注的构造函数、字段和方法的代码。

提取判断子类覆盖父类的方法：

![image-20240814195736380](~/assets/images/spring-di/image-20240814195736380.png)

提取方法，判断子父类方法都被Inject标注

![image-20240814200226834](~/assets/images/spring-di/image-20240814200226834.png)

提取方法，判断子类没有被 Inject 标注

![image-20240814200548328](~/assets/images/spring-di/image-20240814200548328.png)

稍微调整一下，可以得到相似的代码：

![image-20240814202044074](~/assets/images/spring-di/image-20240814202044074.png)

提取方法：

![image-20240814202352826](~/assets/images/spring-di/image-20240814202352826.png)

同样的为了支持Method，需要范型化，而Method 和 Contructor 具有同一个基类 Executable：

![image-20240814201633717](~/assets/images/spring-di/image-20240814201633717.png)

![image-20240814201652190](~/assets/images/spring-di/image-20240814201652190.png)

所以，将提取的方法修改为：

```java
1   private static <T> Object[] toDependencies(Context context, Executable executable) {
2       return Arrays.stream(executable.getParameterTypes())
3               .map(t -> context.get(t).get()).toArray();
4   }
```

修改 Method 的方法：

![image-20240814202727618](~/assets/images/spring-di/image-20240814202727618.png)

将 getArray inline 一下可以实现替换，inline 掉一些方法和变量后，变为：

![Snipaste_2024-08-14_20-30-15](~/assets/images/spring-di/Snipaste_2024-08-14_20-30-15.png)

为了使这块代码看上去更一致，也可以将 Feild 获取依赖的代码提取为方法：

![image-20240814203236723](~/assets/images/spring-di/image-20240814203236723.png)

提取方法，用函数名表达含义，起到了注释的作用，下面的这段代码是用于获取默认构造函数的：

![Snipaste_2024-08-14_20-35-47](~/assets/images/spring-di/Snipaste_2024-08-14_20-35-47.png)

![Snipaste_2024-08-14_20-38-27](~/assets/images/spring-di/Snipaste_2024-08-14_20-38-27.png)

结构类似的方法，如何优化？

以下的两个方法结构非常类似，只是实现不同

![image-20240814204107708](~/assets/images/spring-di/image-20240814204107708.png)

把中间的地方变成一个算法，通过Lambda，把要变化的部分传进去。

先把中间变化的部分提取为方法：

![image-20240814205149449](~/assets/images/spring-di/image-20240814205149449.png)

先修改 getInjectFields 方法：

> 其中使用一个 function 来引用 getList 方法

![image-20240814212142865](~/assets/images/spring-di/image-20240814212142865.png)

同样的，在 getInjectMethods 方法中也用一个 function 来间接引用 getList 方法

![image-20240814212502434](~/assets/images/spring-di/image-20240814212502434.png)

接着，我们可以发现，getInjectMethods 和 getInjectFields 的代码几乎是一样的，除了部分变量的范型不同。

![image-20240814212621229](~/assets/images/spring-di/image-20240814212621229.png)

如果，我们将这两段都提取成一个同名方法，你会发现这两个方法是一样的，除了范型不一样。后续我们希望做到的就是将这两个方法重构为一个方法。

> 仅范型不一样，所以会报错。这里需要先给其中一个方法改为不同的名字。这里先把报红的方法名修改为 traverse1

![image-20240814213050948](~/assets/images/spring-di/image-20240814213050948.png)

接着，修改其中一个方法的签名，也满足两个方法的要求。这里修改 traverse。

将 component 的类型从 `Class<T>` 修改为 `Class<?>`，然后使用范型参数 T 来支持同时接收 Field 和 Method 的参数，并将 injectFields 变量重命名为更加中性的 members ，并将 function 重命名为含义更丰富的 finder

![image-20240815093415791](~/assets/images/spring-di/image-20240815093415791.png)

使用 traverse 替换掉 traverse1 的调用。之后就可以将 traverse1 删掉。

稍微调整，并并通过 inline 重构下面的代码，让其变得更加简洁点：

![image-20240815095344716](~/assets/images/spring-di/image-20240815095344716.png)

其中

```java
1   Arrays.stream(injectConstructor.getParameters()).map(Parameter::getType);
```

可以修改为：

```java
1   Arrays.stream(injectConstructor.getParameterTypes());
```

另外

```java
1   .collect(Collectors.toList())
```

修改为：

```java
1   .toList()
```

再 inline 这些变量：

![image-20240815095814592](~/assets/images/spring-di/image-20240815095814592.png)

# [](#增加新功能-支持注入Provider "增加新功能-支持注入Provider")增加新功能-支持注入Provider

截至到目前为止，我们实现的功能基本上和2003年左右的DI注入容器的功能是差不多的。

> 2003年的 [PicoContainer](http://picocontainer.com/introduction.html) 就基本上和我们当前的功能差不多，Spring 的话还多了更多的对 Configuration 的支持。

接下来需要增加依赖选择相关的功能

```java
1   // 依赖选择相关的测试类
2   @Nested
3   public class DependenciesSelection{
4   
5       @Nested
6       public class ProviderType {
7           // Context
8           // TODO: could get Provider<T> from context
9   
10          // InjectionProvider
11          // TODO：support inject constructor
12          // TODO: support inject field
13          // TODO: support inject method
14      }
15  
16      @Nested
17      public class Qualifier{
18  
19      }
20  
21  }
```

根据任务所属不同的上下文，可以将这些任务列表放到不同的测试中。

将

```java
1   // Context
2   // TODO: could get Provider<T> from context
```

放到 ContextTest 中的 TypeBinding 中

将

```java
1   // InjectionProvider
2   // TODO：support inject constructor
3   // TODO: support inject field
4   // TODO: support inject method
```

分别放到 InjectionTest 中的 ConstructorInjection、FieldInjection、MethodInjection 中。

## [](#从-Context-中获取-Provider "从 Context 中获取 Provider")从 Context 中获取 Provider

> 实现从 Context 中获取 Provider 的功能，是为了后续实现注入 Provider 的功能。
> 
> 作用：
> 
> DI（Dependency Injection，依赖注入）容器中的 `Provider` 模式是一种常见的设计模式，用于延迟实例化依赖项。使用 `Provider` 注入有以下几个主要用途：
> 
> ### [](#1-延迟实例化 "1. 延迟实例化")1\. 延迟实例化
> 
> `Provider` 允许你在**运行时**决定何时创建依赖项的实例。这对于那些耗时较长的初始化过程或资源密集型对象非常有用。例如，如果你有一个数据库连接池，你可能不希望在应用程序启动时就创建所有的连接，而是等到真正需要的时候再创建。
> 
> ### [](#2-控制依赖的生命周期 "2. 控制依赖的生命周期")2\. 控制依赖的生命周期
> 
> 通过 `Provider`，你可以控制依赖项的生命周期。例如，你可以配置一个 `Provider` 使得每次请求都创建一个新的实例（即每次都需要一个全新的对象），或者复用同一个实例（单例模式）。这有助于管理内存使用和资源分配。
> 
> ### [](#3-测试友好 "3. 测试友好")3\. 测试友好
> 
> `Provider` 使测试变得更加容易。在单元测试或集成测试中，你可以轻松地为依赖项提供不同的实现或模拟对象，而不必修改生产代码。
> 
> ### [](#4-动态配置 "4. 动态配置")4\. 动态配置
> 
> 使用 `Provider` 可以让你在运行时根据不同的配置或环境动态地改变依赖项的行为。例如，在开发环境中使用本地数据库，而在生产环境中使用远程数据库。
> 
> ### [](#5-解耦 "5. 解耦")5\. 解耦
> 
> `Provider` 的使用有助于降低代码之间的耦合度。依赖项的创建逻辑与业务逻辑分离，使得代码更易于维护和扩展。
> 
> ### [](#示例-1 "示例")示例
> 
> 假设你有一个 `UserService` 类，它依赖于一个 `DatabaseConnection` 对象。你可以使用 `Provider` 来管理这个依赖关系：
> 
> ```java
> 1   public interface DatabaseConnection {
> 2    void connect();
> 3    void disconnect();
> 4   }
> 5   
> 6   public class UserService {
> 7    private final Provider<DatabaseConnection> dbConnectionProvider;
> 8   
> 9    public UserService(Provider<DatabaseConnection> dbConnectionProvider) {
> 10       this.dbConnectionProvider = dbConnectionProvider;
> 11   }
> 12  
> 13   public void performOperation() {
> 14       DatabaseConnection connection = dbConnectionProvider.get();
> 15       connection.connect();
> 16       // 执行业务逻辑
> 17       connection.disconnect();
> 18   }
> 19  }
> ```
> 
> 在这个例子中，`UserService` 依赖于一个 `DatabaseConnection` 的 `Provider`。每当需要连接到数据库时，`UserService` 就会调用 `dbConnectionProvider.get()` 来获取一个新的连接。这使得 `UserService` 可以灵活地处理连接的创建和关闭，同时也简化了单元测试的实现。
> 
> ### [](#总结-2 "总结")总结
> 
> 使用 `Provider` 注入可以提高代码的灵活性和可测试性，同时还能有效地管理依赖项的生命周期。这在大型应用中特别有用，因为它可以帮助减少内存消耗和提高性能。

我们预期的功能大致如下所示，即希望能从 Context 中获取指定类型的 Provider，但是目前 Java 的范型不支持这种语法。

> Provider 是：jakarta.inject.Provider

![image-20240815144345057](~/assets/images/spring-di/image-20240815144345057.png)

要想实现这个功能，需要先定义一个范型的包装类型：

```java
1   static abstract class TypeLiteral<T> {
2       public ParameterizedType getType() {
3           return (ParameterizedType) ((ParameterizedType)(getClass().getGenericSuperclass()))
4               .getActualTypeArguments()[0];
5       }
6   }
```

> `ParameterizedType` 是 Java 泛型类型的一种表示形式，用于描述带有类型参数的类型（例如 `List<String>`）

如何使用：

```java
1   @Test
2   @Disabled
3   public void java_api() {
4       Component component = new Component() {
5       };
6       ParameterizedType type = new TypeLiteral<Provider<Component>>() {}.getType();
7   
8       assertEquals(Provider.class, type.getRawType());
9       assertEquals(Component.class, type.getActualTypeArguments()[0]);
10  }
```

所以测试，应该如下：

![image-20240815155136365](~/assets/images/spring-di/image-20240815155136365.png)

在 Context 接口中创建这个 get 方法：

![image-20240815155834612](~/assets/images/spring-di/image-20240815155834612.png)

接着在 ContextConfig 中快速实现这个方法，使编译通过：

![image-20240815160013631](~/assets/images/spring-di/image-20240815160013631.png)

现在运行测试，是无法通过的。

实现：

```java
1   @Override
2   public Optional get(ParameterizedType type) {
3       Class<?> componentType = (Class<?>)type.getActualTypeArguments()[0];
4       return Optional.ofNullable(providers.get(componentType))
5               .map(provider -> (Provider<Object>) () -> provider.get(this));
6   }
```

> `.map(provider -> (Provider<Object>) () -> provider.get(this))`: 如果 `providers.get(componentType)` 不为 `null`，那么这里会将找到的提供者转换为一个新的 `Provider<Object>` 实例。这个 lambda 表达式创建了一个新的函数，当被调用时，它通过调用原始提供者的 `get` 方法来获取一个对象实例。注意这里进行了类型转换 `(Provider<Object>)`，这表示期望的结果是一个能够提供 `Object` 类型的提供者。

sad path

```java
1   @Test
2   public void should_not_retrieve_provider_bind_type_as_unsupported_container() {
3       Component component = new Component() {
4       };
5       config.bind(Component.class, component);
6       Context context = config.getContext();
7   
8       ParameterizedType type = new TypeLiteral<List<Component>>(){}.getType();
9   
10      assertFalse(context.get(type).isPresent());
11  }
```

实现：

```java
1   @Override
2   public Optional get(ParameterizedType type) {
3       // 直接校验范型类型是否为 Provider
4       if (type.getRawType() != Provider.class) return Optional.empty();
5       Class<?> componentType = (Class<?>)type.getActualTypeArguments()[0];
6       return Optional.ofNullable(providers.get(componentType))
7               .map(provider -> (Provider<Object>) () -> provider.get(this));
8   }
```

## [](#support-provider-inject-constructor "support provider inject constructor")support provider inject constructor

构造测试：

```java
1   // TODO：support inject constructor
2   static class ProviderInjectConstructor {
3       Provider<Dependency> dependency;
4   
5       @Inject
6       public ProviderInjectConstructor(Provider<Dependency> dependency) {
7           this.dependency = dependency;
8       }
9   }
10  
11  @Test
12  public void should_inject_provider_via_inject_constructor() {
13      ProviderInjectConstructor instance = new InjectionProvider<>(ProviderInjectConstructor.class).get(context);
14  
15      assertNotNull(instance.dependency);
16      assertSame(dependencyProvider, instance.dependency);
17  }
```

因为 InjectionTest 是使用测试替身来进行测试的，所以这里同时还要设置测试替身和 setUp：

![image-20240815170531302](~/assets/images/spring-di/image-20240815170531302.png)

运行测试会在 InjectionProvider 中报异常：

![image-20240815170616411](~/assets/images/spring-di/image-20240815170616411.png)

> 因为这里只能按 Class 的类型获取实例

需要修改为：

> 同时至此 Class 和 ParameterizedType 类型

```java
1   private static <T> Object[] toDependencies(Context context, Executable executable) {
2       return Arrays.stream(executable.getParameters()).map(
3               p -> {
4                   Type type = p.getParameterizedType();
5                   if (type instanceof ParameterizedType) return context.get((ParameterizedType) type).get();
6                   return context.get((Class<?>) type).get();
7               }).toArray();
8   }
```

运行测试，通过。

## [](#support-provider-inject-method "support provider inject method")support provider inject method

```java
1   // TODO: support inject method
2   static class ProviderInjectMethod {
3       Provider<Dependency> dependency;
4   
5       @Inject
6       public void install(Provider<Dependency> dependency) {
7           this.dependency = dependency;
8       }
9   }
10  
11  @Test
12  public void should_inject_provider_via_inject_method() {
13      ProviderInjectMethod instance = new InjectionProvider<>(ProviderInjectMethod.class).get(context);
14  
15      assertNotNull(instance.dependency);
16      assertSame(dependencyProvider, instance.dependency);
17  }
```

运行测试，直接通过。

## [](#support-provider-inject-field "support provider inject field")support provider inject field

构建测试

```java
1   // support provider inject field
2   static class ProviderInjectField {
3       @Inject
4       Provider<Dependency> dependency;
5   }
6   
7   @Test
8   public void should_inject_provider_via_inject_field() {
9       ProviderInjectField instance = new InjectionProvider<>(ProviderInjectField.class).get(context);
10  
11      assertNotNull(instance.dependency);
12      assertSame(dependencyProvider, instance.dependency);
13  }
```

运行测试，以下代码会报错：

```java
1   private static Object toDependency(Context context, Field field) {
2       return context.get(field.getType()).get();
3   }
```

同样是查找依赖的代码异常，修改为：

```java
1   private static Object toDependency(Context context, Field field) {
2       Type type = field.getGenericType();
3       if (type instanceof ParameterizedType) return context.get((ParameterizedType) type).get();
4       return context.get(field.getType()).get();
5   }
```

# [](#遗漏的任务-Provider-依赖的检查 "遗漏的任务-Provider 依赖的检查")遗漏的任务-Provider 依赖的检查

同理，注入 Provider 时也需要检查依赖缺失、循环依赖的情况。

目前，对依赖的检查需要调用 getDependencies 接口，而这里的 getDependencies 接口依然返回的是 Class 类型。我们从容器中寻找依赖时，目前分为两种情况，分别是 Class 和 ，所以这里对依赖缺失或循环依赖的检查可能会出现问题。

```java
1   interface ComponentProvider<T> {
2       T get(Context context);
3   
4       default List<Class<?>> getDependencies() {
5           return List.of();
6       }
7   }
```

以依赖缺失为例，在 ContextTest 中增加测试用例，增加一个参数值：

![image-20240816093648383](~/assets/images/spring-di/image-20240816093648383.png)

```java
1   static class MissingDependencyProviderConstructor implements Component {
2       @Inject
3       public MissingDependencyProviderConstructor(Provider<Dependency> dependency){
4       }
5   }
```

运行，会有一个异常：

![image-20240816093851722](~/assets/images/spring-di/image-20240816093851722.png)

我们期望提示是 Dependency 未找到，而不是 Provider 未找到，或者关于谁的 Provider 未找到，因为当我要求修正错误的时候，也不会去 bind 一个 Provider，而是 bind 一个 Dependency。

在回看 getDependencies 方法，我们期望这里能返回 Class 和 ParameterizedType 的公共接口，即 Type 接口。

```java
1   interface ComponentProvider<T> {
2       T get(Context context);
3   
4       default List<Class<?>> getDependencies() {
5           return List.of();
6       }
7   }
```

这里不能直接修改，需要使用先增加新功能再替换旧功能的方式重构，以下就是预取我们要实现的方式，使用 getDependencyTypes 替换掉 getDependencies：

```java
1   interface ComponentProvider<T> {
2       T get(Context context);
3   
4       default List<Class<?>> getDependencies() {
5           return List.of();
6       }
7   
8       default List<Type> getDependencyTypes() {
9           return List.of();
10      }
11  }
```

补充两个测试用例：

![image-20240816101405554](~/assets/images/spring-di/image-20240816101405554.png)

将这两个测试用例转换为实际的任务测试:

分别在 ConstructorInjection、FieldInjection、MethodInjection 中的 Injection 中增加以下测试

```java
1   // TODO：should include dependency type from inject constructor
2   // TODO：should include dependency type from inject field
3   // TODO：should include dependency type from inject method
```

> 因为修改涉及的步骤比较长，先注释掉测试用例：
> 
> ![Snipaste_2024-08-16_10-26-52](~/assets/images/spring-di/Snipaste_2024-08-16_10-26-52.png)

获取构造器中的依赖的测试：

```java
1   // TODO：should include dependency type from inject constructor
2   @Test
3   public void should_include_dependency_type_from_inject_constructor() {
4       InjectionProvider<ProviderInjectConstructor> provider =
5               new InjectionProvider<>(ProviderInjectConstructor.class);
6   
7       assertArrayEquals(new Type[]{dependencyProviderType}, provider.getDependencyTypes().toArray(Type[]::new));
8   }
```

> 参考前面的 getDependencies 方法，该方法并不检查依赖缺失和循环依赖，但是该方法保证了后续检查的正确性。
> 
> 所以这里的 getDependencyTypes 也是同理。

实现，在 InjectionProvider 中实现这个 getDependencyTypes 方法，与 getDependencies 类似：

![image-20240816110219942](~/assets/images/spring-di/image-20240816110219942.png)

同理，构造字段注入时获取 Provider 依赖类型的测试:

```java
1   // TODO：should include dependency type from inject field
2   @Test
3   public void should_include_provider_dependency_type_from_inject_field() {
4       InjectionProvider<ProviderInjectField> provider =
5               new InjectionProvider<>(ProviderInjectField.class);
6   
7       assertArrayEquals(new Type[]{dependencyProviderType}, provider.getDependencyTypes().toArray(Type[]::new));
8   }
```

实现：

![image-20240816111741157](~/assets/images/spring-di/image-20240816111741157.png)

同理，构造方法注入时获取 Provider 依赖类型的测试:

```java
1   // TODO：should include dependency type from inject method
2   @Test
3   public void should_include_provider_dependency_type_from_inject_method() {
4       InjectionProvider<ProviderInjectMethod> provider = new InjectionProvider<>(ProviderInjectMethod.class);
5   
6       assertArrayEquals(new Type[]{dependencyProviderType}, provider.getDependencyTypes().toArray(Type[]::new));
7   }
```

实现：

![image-20240816112722818](~/assets/images/spring-di/image-20240816112722818.png)

完成 getDependencyTypes 后，就是要使用 getDependencyTypes 来完成依赖缺失的检查。

## [](#Provider-检查依赖缺失 "Provider 检查依赖缺失")Provider 检查依赖缺失

恢复，ContextTest 依赖缺失中的测试用例：

```java
1   static class MissingDependencyProviderConstructor implements Component {
2       @Inject
3       public MissingDependencyProviderConstructor(Provider<Dependency> dependency){
4       }
5   }
```

![Snipaste_2024-08-16_11-30-20](~/assets/images/spring-di/Snipaste_2024-08-16_11-30-20.png)

我们知道，目前检查依赖，并且使用了 getDependencies 方法的地方是 ContextConfig 中的 checkDependencies 方法，这里我们希望将使用 getDependencies 改为使用 getDependencyTypes

![image-20240816113629005](~/assets/images/spring-di/image-20240816113629005.png)

先提取方法：

![image-20240816113543754](~/assets/images/spring-di/image-20240816113543754.png)

使用 Type 替换 Class<?> 并且属于 Class 类型的逻辑依然保持不变：

![image-20240816114253710](~/assets/images/spring-di/image-20240816114253710.png)

被 Provider 包装的类型，需要获取到被包装的依赖的类型，并传递给 DependencyNotFoundException

![image-20240816114722694](~/assets/images/spring-di/image-20240816114722694.png)

目前我们仅实现了对依赖缺失的检查，并没有实现循环依赖的检查（实际上引入 Provider 就解除了循环依赖）。

同理，在 ContextTest 中增加字段注入、方法注入时检查依赖缺失的测试用例。

> 虽然我们已经知道这两个测试会通过，但是还是需要增加这两个测试用例，因为 ContextTest 测试的是比较对外的 API，需要完善测试文档化的诉求。

![image-20240816115431932](~/assets/images/spring-di/image-20240816115431932.png)

```java
1   static class MissingDependencyProviderField implements Dependency {
2       @Inject
3       Provider<Dependency> dependency;
4   }
5   
6   static class MissingDependencyProviderMethod implements Dependency {
7       @Inject
8       public void install(Provider<Dependency> dependency){
9       }
10  }
```

运行测试，直接通过，不用修改生产代码。

## [](#Provider-检查循环依赖 "Provider 检查循环依赖")Provider 检查循环依赖

```java
1   static class CyclicDependencyProviderInjectConstructor implements Dependency {
2       @Inject
3       public CyclicDependencyProviderInjectConstructor(Provider<Component> component) {
4       }
5   }
6   @Test
7   public void should_not_throw_exception_if_cyclic_dependencies_with_provider() {
8       config.bind(Component.class, CyclicComponentInjectConstructor.class);
9       config.bind(Dependency.class, CyclicDependencyProviderInjectConstructor.class);
10  
11      assertTrue(config.getContext().get(Component.class).isPresent());
12  }
```

其中 CyclicComponentInjectConstructor 已经存在

```java
1   static class CyclicComponentInjectConstructor implements Component {
2       @Inject
3       public CyclicComponentInjectConstructor(Dependency dependency) {
4       }
5   }
```

这里的依赖关系是：`Compontent.class` -> `Dependency.class` -> `Provider<Compontent>`

因为 `Provider<Compontent>` 在 `config.bind(Component.class, CyclicComponentInjectConstructor.class);` 时就已经创建，所以这里的依赖循环就解除了。

同理 `Provider<Compontent>` -> `Provider<Dependency>` -> `Provider<Compontent>` 也是如此，引入 Provider 后依赖的循环就解除了：

```java
1   static class CyclicComponentProviderInjectConstructor implements Component {
2       @Inject
3       public CyclicComponentProviderInjectConstructor(Provider<Dependency> dependency) {
4       }
5   }
6   @Test
7   public void should_not_throw_exception_if_cyclic_dependencies_with_providers() {
8       config.bind(Component.class, CyclicComponentProviderInjectConstructor.class);
9       config.bind(Dependency.class, CyclicDependencyProviderInjectConstructor.class);
10  
11      assertTrue(config.getContext().get(Component.class).isPresent());
12  }
```

# [](#重构-5 "重构")重构

获取依赖时的重复代码：

![image-20240816142714821](~/assets/images/spring-di/image-20240816142714821.png)

先修改一下，修改后就完全一样了，可以使用提取方法的重构。

![image-20240816142854828](~/assets/images/spring-di/image-20240816142854828.png)

提取方法后：

![image-20240816143124700](~/assets/images/spring-di/image-20240816143124700.png)

提取后，然后也可以有选择的 inline 掉部分代码，简化代码。

观察 ComponentProvider 中的 getDependencies 发现，这个方法只在测试中用到。

![image-20240816143615349](~/assets/images/spring-di/image-20240816143615349.png)

我们将测试中的调用替换为 getDependencyTypes 发现也没有什么问题。因为 getDependencyTypes 返回的 Type 是 Class 的父接口。

所以可以把这所有 getDependencies 的调用修改为调用 getDependencyTypes，之后可以删除 getDependencies。

同时，将 Class 类型替换为 Type：

![Snipaste_2024-08-16_14-44-20](~/assets/images/spring-di/Snipaste_2024-08-16_14-44-20.png)

## [](#重构对-Type-类型的判断 "重构对 Type 类型的判断")重构对 Type 类型的判断

目前 Context 中有两个接口，分别支持不同的类型：

```java
1   public interface Context {
2       <Type> Optional<Type> get(Class<Type> type);
3   
4       Optional get(ParameterizedType type);
5   }
```

为了支持这两种不同的类型，需要在两个类中的代码的各处做不同的判断，多个 if – else

![image-20240816145441076](~/assets/images/spring-di/image-20240816145441076.png)

![image-20240816145519993](~/assets/images/spring-di/image-20240816145519993.png)

那么当需要对这种结构的类型做修改的话，很可能就会发生**散弹式修改**。

> 很多时候，我们对代码不是很满意，但是又不知道如何下手修改。
> 
> 这个时候可以考虑将相关功能的散落在各处的坏味道的代码集中到同一个上下文中。

比如说，InjectionProvider 中的 toDependency 方法是根据类型判断调用 Context 接口中的哪个方法的：

```java
1   private static Object toDependency(Context context, Type type) {
2       if (type instanceof ParameterizedType) return context.get((ParameterizedType) type).get();
3       return context.get((Class<?>) type).get();
4   }
```

那么可以将这个实现移动到 Context 接口的默认方法中去：

```java
1   public interface Context {
2       <Type> Optional<Type> get(Class<Type> type);
3   
4       Optional get(ParameterizedType type);
5   
6       default Optional getType(Type type) {
7           if (type instanceof ParameterizedType) return get((ParameterizedType) type);
8           return get((Class<?>) type);
9       }
10  }
```

那 toDependency 就可以改为：

```java
1   private static Object toDependency(Context context, Type type) {
2       return context.getType(type).get();
3   }
```

运行测试，会有异常，这是在 InjectionTest 使用测试替身引起的，我们之前的测试替身是调用的是 Context 的 get 方法，但是修改代码后调用的是 Context 的 getType 方法，所以需要同步修改测试替身，修改为调用 getType 方法。

![image-20240816151832369](~/assets/images/spring-di/image-20240816151832369.png)

> 用测试替身还是用真实的待测组件？
> 
> 当你接口约定稳定的时候，那么用 stub 会更简单。所以测试替身需要知道待测组件内部的实现，当内部实现修改时，可能造成测试失败。所以这种使用测试替身的伦敦学派测试，对重构的影响比较大。

之后在 ContextConfig 中实现这个方法，就可以将接口的默认方法恢复为未实现的普通方法：

![image-20240816152614060](~/assets/images/spring-di/image-20240816152614060.png)

至此，我们就将对这两类型的判断相关的代码，都移动到了 ContextConfig 这个上下文中。

再然后，查看一下还有哪里在使用 Context 的 get 接口，可以发现，除了 ContextConfig 中使用外，就是在测试方法中使用。

我们把这些测试中使用 get 的地方都改成 getType，也不会异常。

那么 get 方法就只在 ContextConfig 中被使用了，这样就可以把 Context 接口中的 get 方法移除掉，并移除到 ContextConfig 中的 Override 注解并且设置为 private，只保留一个 getType 方法作为对外的API：

![Snipaste_2024-08-16_15-43-32](~/assets/images/spring-di/Snipaste_2024-08-16_15-43-32.png)

再将 getType 重命名为 get。

至此，我们就实现了使用一个接口替换为原来的两个接口的效果。

继续重构，先使用函数来代替注释

![Snipaste_2024-08-16_15-53-25](~/assets/images/spring-di/Snipaste_2024-08-16_15-53-25.png)

> 这里的 ContainerType 的含义是比如：List<>、Provider<> 这些容器。

重命名方法：

![image-20240816160853947](~/assets/images/spring-di/image-20240816160853947.png)

提取方法

![Snipaste_2024-08-16_16-09-16](~/assets/images/spring-di/Snipaste_2024-08-16_16-09-16.png)

在修改一下提取的方法的参数：

```java
1   private static Class<?> getComponentType(Type type) {
2       return (Class<?>) ((ParameterizedType)type).getActualTypeArguments()[0];
3   }
```

再修改一下 checkDependencies 中的代码：

![image-20240816161944872](~/assets/images/spring-di/image-20240816161944872.png)

至此我们会发现，整个 ContextConfig 就是围绕两个不同的 Type 来做判断，并实现功能的。

出现这种情况的话，通常都意味着封装失败。造成这种情况都是因为我们使用了一些我们无法修改，无法增加行为的类和接口（可能是由其他框架或库提供的，也可能是JDK中的）。

> 在实践中，有些时候不要使用原始类型（Primitive Type），并不是指不使用 int 而是使用 Integer，而是说所有我们无法修改的类都是原始类型。

## [](#封装-Type-类型的判断逻辑 "封装 Type 类型的判断逻辑")封装 Type 类型的判断逻辑

因为我们使用的是原始类型，在我们的上下文中代表某个概念。这种概念一般会有概念缺失（Concept Missing）。

不仅仅是在代码层面上重构，其实是要从模型的角度上重构。正是因为使用了这种内容缺失的概念，以至于每次使用到这种概念的时候，需要对它进行复杂的判断。

对于这种概念缺失的优化呢，就是使用封装，一般有两种封装方式，分别是：行为封装、数据封装。

？？？？

这里使用数据封装

对代码进行稍微的整理，会发现，这些对 Type 进行判断的代码中，都会包含 componentType 或 ContainerType 或两者同时包含。

![image-20240816172206505](~/assets/images/spring-di/image-20240816172206505.png)

新建一个封装类：

```java
1   static class Ref {
2       private Type container;
3       private Class<?> component;
4   
5       Ref(ParameterizedType type) {
6           this.container = type.getRawType();
7           this.component = (Class<?>) type.getActualTypeArguments()[0];
8       }
9   
10      Ref(Class<?> component) {
11          this.component = component;
12      }
13  
14      static Ref of(Type type) {
15          if (type instanceof ParameterizedType) return new Ref((ParameterizedType) type);
16          return new Ref((Class<?>) type);
17      }
18  
19      public Type getContainer() {
20          return container;
21      }
22  
23      public Class<?> getComponent() {
24          return component;
25      }
26  }
```

接着就可以使用 Ref 来代替 type 的表示。

![image-20240816172730553](~/assets/images/spring-di/image-20240816172730553.png)

这两个方法，只有在 Context 的 get 方法中被调用，因为使用了 Ref 代替了两种不同的类型，所以不需要分两个方法进行判断了，这里先 inline 这个两个方法。

inline 并整理一下代码后，得到下面的代码结构：

![image-20240816173312128](~/assets/images/spring-di/image-20240816173312128.png)

其中

```java
1   if (isContainerType(type)) { ... }
```

的判断，我们应该把其作为 Ref 的知识，封装到 Ref 中，在 Ref 新增 接口：

```java
1   public boolean isContainer() {
2       return container != null;
3   }
```

那么这个判断语句就可以改为：

```java
1   if (ref.isContainer())
```

同理，使用 Ref 代替 checkXXXDependencies 中的 type 引用：

![image-20240816174437894](~/assets/images/spring-di/image-20240816174437894.png)

inline 这两个方法，inline 并调整简化代码后，变成如下：

```java
1   private void checkDependencies(Class<?> component, Stack<Class<?>> visiting) {
2       for (Type dependency : providers.get(component).getDependencyTypes()) {
3           Ref ref = Ref.of(dependency);
4           // 如果依赖的类型不存在，就提前停止递归
5           if (!providers.containsKey(ref.getComponent())) throw new DependencyNotFoundException(component, ref.getComponent());
6           if (!ref.isContainer()) {
7               if (visiting.contains(ref.getComponent())) throw new CyclicDependenciesException(visiting);
8               visiting.push(ref.getComponent());
9               checkDependencies(ref.getComponent(), visiting);
10              visiting.pop();
11          }
12      }
13  }
```

移除代码：

![Snipaste_2024-08-16_17-56-56](~/assets/images/spring-di/Snipaste_2024-08-16_17-56-56.png)

将 Ref 从内部类中移出。

## [](#Context-使用-Ref-对外提供访问 "Context 使用 Ref 对外提供访问")Context 使用 Ref 对外提供访问

我们希望在 Context接口中，使用 Ref 代替 Type：

```java
1   public interface Context {
2       Optional get(Type type);
3   
4       Optional get(Ref ref);
5   }
```

抽取 get 方法，并Override

![image-20240817094941953](~/assets/images/spring-di/image-20240817094941953.png)

这里也可以将 get(Type type) 方法改为default

```java
1   public interface Context {
2       default Optional get(Type type) {
3           return get(Ref.of(type));
4       }
5   
6       Optional get(Ref ref);
7   }
```

将 Ref 移入 Context 中。

尝试直接inline `Optional get(Type type)`方法。

inline 后，使用测试替身的地方又会报错，原因是：inline 后 eq 的位置是错误的，需要人工修改一下

![image-20240817100143695](~/assets/images/spring-di/image-20240817100143695.png)

修改为：

![image-20240817100436322](~/assets/images/spring-di/image-20240817100436322.png)

此外还需要在 Ref 中增加 equals 和 hashCode方法。

至此，对 Context 的访问都是通过 Ref 参数访问。

接着，需要将 ComponentProvider 中的 getDependencyTypes 方法修改为返回 List

```java
1   interface ComponentProvider<T> {
2       T get(Context context);
3   
4       default List<Type> getDependencyTypes() {
5           return List.of();
6       }
7   }
```

同理，也需要新增，再替换

```java
1   interface ComponentProvider<T> {
2       T get(Context context);
3   
4       default List<Type> getDependencyTypes() {
5           return List.of();
6       }
7   
8       default List<Context.Ref> getDependencies() {
9           return getDependencyTypes().stream().map(Context.Ref::of).toList();
10      }
11  }
```

查看 getDependencyTypes 在哪里被使用，并尝试人工替换

![image-20240817101707744](~/assets/images/spring-di/image-20240817101707744.png)

修改测试中的使用，把所有的使用修改为类似以下形式：

![image-20240817102416259](~/assets/images/spring-di/image-20240817102416259.png)

接着就是要将旧的 `List<Type> getDependencyTypes()` 移出掉。

实现 getDependencies 方法

![image-20240817103155965](~/assets/images/spring-di/image-20240817103155965.png)

inline 并删除 getDependencyTypes 实现

![image-20240817103405954](~/assets/images/spring-di/image-20240817103405954.png)

getDependencies 还是要保留默认实现

```java
1   interface ComponentProvider<T> {
2       T get(Context context);
3   
4       default List<Context.Ref> getDependencies() {
5           return List.of();
6       }
7   }
```

## [](#如何让接口-API-变得更友好 "如何让接口 API 变得更友好")如何让接口 API 变得更友好

目前的 API 功能都是正确的，但是从使用者的角度看就并不友好

```java
1   public interface Context {
2   
3       Optional get(Ref ref);
4       
5       ....
6   }
```

现在 Context 中 get 方法的入参和返回值都是不带范型的。

那么有些时候，就还需要使用者自己来做型转

![image-20240817110150540](~/assets/images/spring-di/image-20240817110150540.png)

增加范型支持：

![Snipaste_2024-08-17_11-10-00](~/assets/images/spring-di/Snipaste_2024-08-17_11-10-00.png)

那么这个时候再 get 时，就能直接指示类型

![image-20240817111102232](~/assets/images/spring-di/image-20240817111102232.png)

> 因为：
> 
> ```plaintext
> 1   Class<Component> component1 = Component.class;
> ```

现在就让 API 变得更容易，减少不必要的型转。

> 在 get 方法中增加对范型的支持
> 
> ![image-20240819105209273](~/assets/images/spring-di/image-20240819105209273.png)

上面的范型是对Class<?>的参数提供的支持，那么如何支持ContainerType的情况呢？

目前支持 ContainerType 的参数的方法是：

```java
1   static Ref of(Type type) {
2       if (type instanceof ParameterizedType) {
3           return new Ref((ParameterizedType) type);
4       }
5       return new Ref((Class<?>) type);
6   }
```

并且在使用时，还需要用自定义的 `TypeLiteral` 包装一下：

![image-20240817112312997](~/assets/images/spring-di/image-20240817112312997.png)

一个可能的方法是，将 Ref 和 TypeLiteral 做一个整合，以达到类似如下的使用效果：

```java
1   context.get(new Context.Ref<Provider<Component>>() {});
```

这里是创建一个匿名的 Ref 实例，如果我们获取去到这个实例的类型并为 Ref 中必要的字段赋值，可以避免用户在时使用自己构造TypeLiteral。

这里需要先创建一个无参构造函数，并在函数中获取到这个实例的范型类型，并根据范型类型赋值 Ref 的字段。

```java
1   protected Ref () {
2       Type type = ((ParameterizedType)(getClass().getGenericSuperclass())).getActualTypeArguments()[0];
3       init(type);
4   }
5   
6   private void init(Type type) {
7       if (type instanceof ParameterizedType) {
8           this.container = ((ParameterizedType) type).getRawType();
9           this.component = (Class<?>) ((ParameterizedType) type).getActualTypeArguments()[0];
10      } else {
11          this.component = (Class<?>) type;
12      }
13  }
```

这里提取了 init 方法，那么也可以将原来的有参构造函数的实现委托给 init 方法：

```java
1   Ref(ParameterizedType type) {
2       init(type);
3   }
4   
5   Ref(Class<ComponentType> component) {
6       init(component);
7   }
8   
9   protected Ref () {
10      Type type = ((ParameterizedType)(getClass().getGenericSuperclass())).getActualTypeArguments()[0];
11      init(type);
12  }
13  
14  private void init(Type type) {
15      if (type instanceof ParameterizedType) {
16          this.container = ((ParameterizedType) type).getRawType();
17          this.component = (Class<?>) ((ParameterizedType) type).getActualTypeArguments()[0];
18      } else {
19          this.component = (Class<?>) type;
20      }
21  }
```

那么测试类中使用时，就修改为：

![image-20240817115223561](~/assets/images/spring-di/image-20240817115223561.png)

随后就可以删除 TypeLiteral 了。

# [](#Qualifier "Qualifier")Qualifier

自定义 Qualifier 的依赖

*   注册组件时，可额外指定 Qualifier
    
*   注册组件时，可从类对象上提取 Qualifier
    
*   寻找依赖时，需同时满足类型与自定义 Qualifier 标注
    
*   支持默认 Qualifier——Named
    

将上面的功能点，细分为多个测试任务

归属于 ContextTest 上下文中的任务，分别有关于 TypeBinding 和 DependencyCheck 的任务：

TypeBinding 的任务：

```java
1   @Nested
2   public class WithQualifier {
3       // TODO binding component with qualifier
4       // TODO binding component with qualifiers
5       // TODO throw illegal component if illegal qualifier
6   }
```

DependencyCheck 的任务：

```java
1   @Nested
2   public class WithQualifier {
3       // TODO dependency missing if qualifier not match
4       // TODO check cyclic dependencies with qualifier
5   }
```

归属于 InjectionTest 上下文中的任务，分别有关于 ConstructorInjection、FieldInjection、MethodInjection 的任务：

分别都有如下的测试任务：

```java
1   @Nested
2   class WithQualifier {
3       // TODO inject with qualifier
4       // TODO throw illegal component if illegal qualifier given to injection point
5   }
```

## [](#binding-component-with-qualifier "binding component with qualifier")binding component with qualifier

component 分为两种情况，分别是：instance 和 component。

### [](#绑定-instance "绑定 instance")绑定 instance

先实现 instance 的情况，创建测试：

```java
1   // TODO binding component with qualifier
2   @Test
3   public void should_bind_instance_with_qualifier() {
4       Component component = new Component() {
5       };
6       config.bind(Component.class, component, new NamedLiteral("ChosenOne"));
7   
8       Context context = config.getContext();
9   
10      Component chosenOne =
11              context.get(Context.Ref.of(Component.class, new NamedLiteral("ChosenOne"))).get();
12      assertSame(component, chosenOne);
13  }
```

需要新建 NamedLiteral

```java
1   record NamedLiteral(String value) implements jakarta.inject.Named {
2       @Override
3       public Class<? extends Annotation> annotationType() {
4           return jakarta.inject.Named.class;
5       }
6   }
```

并且需要在 ContextConfig 中增加包含三个参数的 bind 方法

```java
1   public <Type> void bind(Class<Type> type, Type instance, Annotation qualifier) {
2   }
```

在 Ref 中增加两个参数的 of 方法：

```java
1   static <ComponentType> Ref<ComponentType> of(Class<ComponentType> component, Annotation qualifier) {
2       return null;
3   }
```

使得编译通过。

实现

目前，保存 providers 的 map 中的 key 只有 class，我们现在需要的是 type 和 qualifier 两个参数共同组合成的 key

![image-20240819104016654](~/assets/images/spring-di/image-20240819104016654.png)

自定义一个 record 来封装 type 和 qualifier 的组合。

```java
1   record Component(Class<?> type, Annotation qualifier) {
2   }
```

并新建一个 map 来保存

```java
1   private Map<Component, ComponentProvider<?>> components = new HashMap<>();
```

实现 bind 方法：

```java
1   public <Type> void bind(Class<Type> type, Type instance, Annotation qualifier) {
2       components.put(new Component(type, qualifier), context -> instance);
3   }
```

get 时需要判断 Ref 中是否是 Qualifier 的情况

可以在在 Ref 中增加一个字段 qualifier ，并相应的在构造方法中增加字段：

```java
1   private Annotation qualifier;
2   
3   Ref(Type type, Annotation qualifier) {
4       init(type);
5       this.qualifier = qualifier;
6   }
7   
8   public Annotation getQualifier() {
9       return qualifier;
10  }
```

新增分支，从 Context 中获取实例

![Snipaste_2024-08-19_11-18-32](~/assets/images/spring-di/Snipaste_2024-08-19_11-18-32.png)

运行测试，通过。

### [](#绑定组件 "绑定组件")绑定组件

构造测试

```java
1   @Test
2   public void should_bind_component_with_qualifier() {
3       Dependency dependency = new Dependency() {
4       };
5       config.bind(Dependency.class, dependency);
6       config.bind(ConstructorInjection.class, ConstructorInjection.class, new NamedLiteral("ChosenOne"));
7   
8       Context context = config.getContext();
9   
10      ConstructorInjection chosenOne =
11              context.get(Context.Ref.of(ConstructorInjection.class, new NamedLiteral("ChosenOne"))).get();
12      assertSame(dependency, chosenOne.dependency());
13  }
```

```java
1   static class ConstructorInjection implements Component {
2       private Dependency dependency;
3   
4       @Inject
5       public ConstructorInjection(Dependency dependency) {
6           this.dependency = dependency;
7       }
8   
9       @Override
10      public Dependency dependency() {
11          return dependency;
12      }
13  }
```

需要增加一个对应的 bind 方法：

```java
1   public <Type, Implementation extends Type>
2   void bind(Class<Type> type, Class<Implementation> implementation, Annotation qualifier) {
3       components.put(new Component(type, qualifier), new InjectionProvider(implementation));
4   }
```

运行测试，通过。

## [](#binding-component-with-qualifiers "binding component with qualifiers")binding component with qualifiers

绑定、注册组件的时候，可以指定多个 qualifier，但是只能根据一个取，这是规范规定的。

### [](#绑定实例 "绑定实例")绑定实例

```java
1   // TODO binding component with qualifiers
2   @Test
3   public void should_bind_instance_with_multi_qualifiers() {
4       Component component = new Component() {
5       };
6       config.bind(Component.class, component, new NamedLiteral("ChosenOne"), new NamedLiteral("AnotherOne"));
7   
8       Context context = config.getContext();
9   
10      Component chosenOne = context.get(Context.Ref.of(Component.class, new NamedLiteral("ChosenOne"))).get();
11      Component anotherOne = context.get(Context.Ref.of(Component.class, new NamedLiteral("AnotherOne"))).get();
12  
13      assertSame(component, anotherOne);
14      assertSame(chosenOne, anotherOne);
15  }
```

将 bind 方法的 qualifier 参数修改为可变数组，使编译通过：

```java
1   public <Type> void bind(Class<Type> type, Type instance, Annotation... qualifiers) {
2       components.put(new Component(type, qualifiers[0]), context -> instance);
3   }
```

实现，bind 时分别注册每一 qualifier

```java
1   public <Type> void bind(Class<Type> type, Type instance, Annotation... qualifiers) {
2       for (Annotation qualifier : qualifiers)
3           components.put(new Component(type, qualifier), context -> instance);
4   }
```

### [](#绑定组件-1 "绑定组件")绑定组件

构造测试

```java
1   @Test
2   public void should_bind_component_with_multi_qualifiers() {
3       Dependency dependency = new Dependency() {
4       };
5       config.bind(Dependency.class, dependency);
6       config.bind(ConstructorInjection.class, ConstructorInjection.class, new NamedLiteral("ChosenOne"),
7               new NamedLiteral("AnotherOne"));
8   
9       Context context = config.getContext();
10  
11      ConstructorInjection chosenOne =
12              context.get(Context.Ref.of(ConstructorInjection.class, new NamedLiteral("ChosenOne"))).get();
13       ConstructorInjection anotherOne =
14               context.get(Context.Ref.of(ConstructorInjection.class, new NamedLiteral("AnotherOne"))).get();
15  
16      assertSame(dependency, chosenOne.dependency());
17      assertSame(dependency, anotherOne.dependency());
18  }
```

实现，对应的为 bind 方法的 qualifier 参数修改为可变数组，并分别注册每一个 qualifier ：

```java
1   public <Type, Implementation extends Type>
2   void bind(Class<Type> type, Class<Implementation> implementation, Annotation... qualifiers) {
3       for (Annotation qualifier : qualifiers)
4           components.put(new Component(type, qualifier), new InjectionProvider(implementation));
5   }
```

## [](#重构-ContextConfig-的内部实现 "重构 ContextConfig 的内部实现")重构 ContextConfig 的内部实现

位置支持 Qualifier 我们目前已经有很多方法存在平行实现（实现方法非常类似），如果继续完成其他测试，那么会产生更多的平行实现。这里我们选择先重构。

### [](#components-替换掉-providers "components 替换掉 providers")components 替换掉 providers

接下来，就是要用 components 替换掉 providers

```java
1   private Map<Class<?>, ComponentProvider<?>> providers = new HashMap<>();
2   
3   private Map<Component, ComponentProvider<?>> components = new HashMap<>();
```

重构之前先看一下有哪些地方使用了 providers

![Snipaste_2024-08-19_14-16-56](~/assets/images/spring-di/Snipaste_2024-08-19_14-16-56.png)

这里使用的主要地方是 getContext 和 checkDependencies。

先看 getContext

![Snipaste_2024-08-19_14-20-19](~/assets/images/spring-di/Snipaste_2024-08-19_14-20-19.png)

先将其中使用到 providers 的位置提取为方法：

```java
1   private <ComponentType> ComponentProvider<?> getComponentProvider(Context.Ref<ComponentType> ref) {
2   //        components.get(new Component(ref.getComponent(), ref.getQualifier()));
3       return providers.get(ref.getComponent());
4   }
```

上面注释的代码，就是我们预期想要的实现。

逐步将使用到 providers 的地方用 components 替换掉。

bind 方法中替换：

```java
1   public <Type> void bind(Class<Type> type, Type instance) {
2   //        providers.put(type, (ComponentProvider<Type>) context -> instance);
3       components.put(new Component(type, null), context -> instance);
4   }
5   
6   public <Type, Implementation extends Type>
7   void bind(Class<Type> type, Class<Implementation> implementation) {
8   //        providers.put(type, new InjectionProvider(implementation));
9       components.put(new Component(type, null), new InjectionProvider(implementation));
10  }
```

getContext 方法替换：

![image-20240819144934546](~/assets/images/spring-di/image-20240819144934546.png)

![image-20240819145015046](~/assets/images/spring-di/image-20240819145015046.png)

至此移除不在使用的 providers 即可。

> 观察以下两个 bind 方法，可以合并成一个
> 
> ```java
> 1   public <Type> void bind(Class<Type> type, Type instance) {
> 2       components.put(new Component(type, null), context -> instance);
> 3   }
> 4   
> 5   public <Type> void bind(Class<Type> type, Type instance, Annotation... qualifiers) {
> 6       for (Annotation qualifier : qualifiers)
> 7           components.put(new Component(type, qualifier), context -> instance);
> 8   }
> ```
> 
> 合并后为：
> 
> ```java
> 1   public <Type> void bind(Class<Type> type, Type instance, Annotation... qualifiers) {
> 2       if (qualifiers.length == 0) components.put(new Component(type, null), context -> instance);
> 3       for (Annotation qualifier : qualifiers)
> 4           components.put(new Component(type, qualifier), context -> instance);
> 5   }
> ```
> 
> **建议不合并**，减少一个 if 也可以有一个更清晰的对外接口。

### [](#其他坏味道 "其他坏味道")其他坏味道

可以观察到，很多使用 Ref 的地方都需要转换为 Component

![image-20240819150104089](~/assets/images/spring-di/image-20240819150104089.png)

好像 Ref 和 Component 之间存在某种关系。

其实，Ref 就应该将 Class 和 Qualifier 封装为一个整体，而不是再将这两个拆散。

一个更合理的实现是，使用一个 Component 来替换掉 `Class<?> component` 和 `Annotation qualifier` 字段：

```java
1   class Ref<ComponentType> {
2       private Type container;
3   //        private ContextConfig.Component component;
4       private Class<?> component;
5       private Annotation qualifier;
6   }
```

这里先将 Ref 重名为 ComponentRef，并从 Context 中移出，作为一个外部类。

也将 Component 从 ContextConfig 中移出，作为一个外部类。

> 由于原来已经有一个 Component 用于作为测试用例的类，这里先将原来的 Component 修改为 TestComponent，以避免因重名造成的异常。

在 ComponentRef 中增加 component 字段，并将原来的 component 字段重命名为 componentType：

```java
1   public class ComponentRef<ComponentType> {
2       private Type container;
3       private Component component;
4       private Class<?> componentType;
5       private Annotation qualifier;
6   }
```

增加一个 component 字段，相应的给 init 中增加一个 qualifier 的参数，并在其中为 component 赋值。

```java
1   private void init(Type type, Annotation qualifier) {
2       if (type instanceof ParameterizedType) {
3           this.container = ((ParameterizedType) type).getRawType();
4           this.componentType = (Class<?>) ((ParameterizedType) type).getActualTypeArguments()[0];
5           this.component = new Component(componentType, qualifier);
6       } else {
7           this.componentType = (Class<?>) type;
8           this.component = new Component(componentType, qualifier);
9       }
10  }
```

那么所有之前通过 ref 来 new Component 都可以替换为 ref.component().

![image-20240819155305967](~/assets/images/spring-di/image-20240819155305967.png)

还可以发现，getQualifier 已无处使用，可以移除，qualifier 字段也无处使用，可以移除。

同时也可将 getComponentType 的实现替换为如下：

```java
1   public Class<?> getComponentType() {
2       return component.type();
3   }
```

接着，期望移除 component，先找到 component 在哪里被使用。

一个地方是在 equals 和 hashCode 方法中被使用，先重新生成这两个方法，新生成的方法不要使用 componentType 字段。

其他使用的地方就是在 init 方法中，修改 init 方法为：

```java
1   private void init(Type type, Annotation qualifier) {
2       if (type instanceof ParameterizedType) {
3           this.container = ((ParameterizedType) type).getRawType();
4           Class<?> componentType = (Class<?>) ((ParameterizedType) type).getActualTypeArguments()[0];
5           this.component = new Component(componentType, qualifier);
6       } else {
7           this.component = new Component((Class<?>) type, qualifier);
8       }
9   }
```

移除 componentType 字段。

## [](#重构测试 "重构测试")重构测试

### [](#测试文档化-1 "测试文档化")测试文档化

从测试文档化的角度来讲，下面的两个测试是不需要的。

![image-20240819161618368](~/assets/images/spring-di/image-20240819161618368.png)

这两个测试，是驱动我们开发的记录，但是不应该作为最终的文档形式。

### [](#自定义-Qualifier "自定义 Qualifier")自定义 Qualifier

```java
1   @java.lang.annotation.Documented
2   @java.lang.annotation.Retention(RUNTIME)
3   @jakarta.inject.Qualifier
4   @interface AnotherOne {
5   }
6   
7   record AnotherOneLiteral() implements AnotherOne {
8       @Override
9       public Class<? extends Annotation> annotationType() {
10          return AnotherOne.class;
11      }
12  }
```

bind 时使用自定义注解：

![image-20240819162836708](~/assets/images/spring-di/image-20240819162836708.png)

## [](#非法的-Qualifier "非法的 Qualifier")非法的 Qualifier

验证的是非 Qualifier 注解标记的情况。

需要先创建一个非 Qualifier 的注解的包装

```java
1   record TestLiteral() implements Test {
2       @Override
3       public Class<? extends Annotation> annotationType() {
4           return Test.class;
5       }
6   }
```

*   构造绑定实例的测试：

```java
1   // TODO throw illegal component if illegal qualifier
2   @Test
3   public void should_throw_exception_if_illegal_qualifier_given_to_instance() {
4       TestComponent component = new TestComponent() {
5       };
6       assertThrows(IllegalComponentException.class, () -> config.bind(TestComponent.class, component, new TestLiteral()));
7   }
```

实现，绑定时检查是否包含非Qualifier的注解：

```java
1   public <Type> void bind(Class<Type> type, Type instance, Annotation... qualifiers) {
2       if (Arrays.stream(qualifiers).anyMatch(q -> !q.annotationType().isAnnotationPresent(Qualifier.class)))
3           throw new IllegalComponentException();
4       for (Annotation qualifier : qualifiers)
5           components.put(new Component(type, qualifier), context -> instance);
6   }
```

*   构造绑定组件的测试：

```java
1   @Test
2   public void should_throw_exception_if_illegal_qualifier_given_to_component() {
3       assertThrows(IllegalComponentException.class, 
4               () -> config.bind(ConstructorInjection.class, ConstructorInjection.class, new TestLiteral()));
5   }
```

实现，同样的绑定时检查是否包含非Qualifier的注解：

```java
1   public <Type, Implementation extends Type>
2   void bind(Class<Type> type, Class<Implementation> implementation, Annotation... qualifiers) {
3       if (Arrays.stream(qualifiers).anyMatch(q -> !q.annotationType().isAnnotationPresent(Qualifier.class)))
4           throw new IllegalComponentException();
5       for (Annotation qualifier : qualifiers)
6           components.put(new Component(type, qualifier), new InjectionProvider(implementation));
7   }
```

## [](#依赖检查 "依赖检查")依赖检查

### [](#Qualifier-标记的依赖不存在 "Qualifier 标记的依赖不存在")Qualifier 标记的依赖不存在

测试指定了 Qualifier 的依赖的情况：

> 如果依赖的参数被 Qualifier 标记，那么从 容器中获取的依赖也必须被 Qualifier 标记，否则也要抛出 DependencyNotFoundException 异常。

```java
1   // TODO dependency missing if qualifier not match
2   @Test
3   public void should_throw_exception_if_dependency_not_found_with_qualifier() {
4   
5       config.bind(Dependency.class, new Dependency() {
6       });
7       config.bind(InjectConstructor.class, InjectConstructor.class);
8   
9       assertThrows(DependencyNotFoundException.class, () -> config.getContext());
10  
11  }
12  
13  static class InjectConstructor {
14      @Inject
15      public InjectConstructor(@AnotherOne Dependency dependency) {
16      }
17  }
```

目前的依赖检查的实现是基于 CompronentProvider 中的 getDependencies 方法。

![image-20240819171549770](~/assets/images/spring-di/image-20240819171549770.png)

但是目前获取依赖时并没有区分被 Qualifier 标记的情况。所以想要实现依赖缺失的检查还需要修改 CompronentProvider 中的 getDependencies 方法。

这样就衍生出，`include qualifier with dependency` 的测试。这属于 InjectionTest 测试上下文的范畴。

分别在 InjectionTest 的 ConstructorInjection、FieldInjection、MethodInjection 中的 WithQualifier 测试分组中增加任务：

![Snipaste_2024-08-19_17-25-58](~/assets/images/spring-di/Snipaste_2024-08-19_17-25-58.png)

构造函数注入被 Qualifier 标注的测试：

```java
1   // TODO include qualifier with dependency
2   static class InjectConstructor {
3       @Inject
4       public InjectConstructor(@Named("ChosenOne") Dependency dependency) {
5       }
6   }
7   @Test
8   public void should_include_qualifier_with_dependency() {
9       InjectionProvider<InjectConstructor> provider = new InjectionProvider<>(InjectConstructor.class);
10  
11      assertArrayEquals(new ComponentRef[]{ComponentRef.of(Dependency.class, new NamedLiteral("ChosenOne"))},
12              provider.getDependencies().toArray(ComponentRef[]::new));
13  }
```

实现，需要修改以下代码：

```java
1   @Override
2   public List<ComponentRef> getDependencies() {
3       return Stream.concat(
4                       Stream.concat(Arrays.stream(injectConstructor.getParameters()).map(Parameter::getParameterizedType),
5                               injectFields.stream().map(Field::getGenericType)),
6                       injectMethods.stream().flatMap(m -> Arrays.stream(m.getGenericParameterTypes())))
7               .map(ComponentRef::of).toList();
8   }
```

目前并没有考虑标注的情况。

修改 Provider 中的实现，获取依赖时在返回的 ComponentRef 应包含注解的信息。

![image-20240819180342402](~/assets/images/spring-di/image-20240819180342402.png)

此外，判断 Named 于 NamedLiteral 是否相等，还需要修改 NamedLiteral 中的 equals 方法，因为是测试，所以只需要一个简单的实现。

> 如果是生产代码中，应该根据 Annotation 中规范的方式编写。

```java
1   @Override
2   public boolean equals(Object o) {
3       if (o instanceof jakarta.inject.Named named) return value.equals(named.value());
4       return false;
5   }
```

运行测试通过。

同时，`should_throw_exception_if_dependency_not_found_with_qualifier` 测试也将通过。

### [](#DependencyNotFoundException-信息优化 "DependencyNotFoundException 信息优化")DependencyNotFoundException 信息优化

目前 DependencyNotFoundException 中并不包含 Qualifier 注解的信息。

```java
1   public class DependencyNotFoundException extends RuntimeException {
2       private Class<?> dependency;
3       private Class<?> component;
4   
5       public DependencyNotFoundException(Class<?> component, Class<?> dependency) {
6           this.dependency = dependency;
7           this.component = component;
8       }
9   
10      public Class<?> getDependency() {
11          return dependency;
12      }
13  
14      public Class<?> getComponent() {
15          return component;
16      }
17  }
```

如果我们还需要知道异常中注解的信息，可以修改测试，增加如下校验：

![image-20240819183725309](~/assets/images/spring-di/image-20240819183725309.png)

在 DependencyNotFoundException 中新建两个方法，分别用于获取造成异常的 component 和 dependency 的信息。

DependencyNotFoundException 重构为：

> 增加两个 Component 类型的字段和对应的 getter，以及构造函数。

```java
1   public class DependencyNotFoundException extends RuntimeException {
2       private Class<?> dependency;
3       private Class<?> component;
4       private Component dependencyComponent;
5       private Component componentComponent;
6   
7       public DependencyNotFoundException(Class<?> component, Class<?> dependency) {
8           this.dependency = dependency;
9           this.component = component;
10      }
11  
12      public DependencyNotFoundException(Component componentComponent, Component dependencyComponent) {
13          this.dependencyComponent = dependencyComponent;
14          this.componentComponent = componentComponent;
15      }
16  
17      public Class<?> getDependency() {
18          return dependency;
19      }
20  
21      public Class<?> getComponent() {
22          return component;
23      }
24  
25      public Component getDependencyComponent() {
26          return this.dependencyComponent;
27      }
28  
29      public Component getComponentComponent() {
30          return this.componentComponent;
31      }
32  }
```

同样的 AnotherOneLiteral 也需要实现 equals 方法，否则 AnotherOneLiteral 和 AnotherOne 的比较会异常

```java
1   record AnotherOneLiteral() implements AnotherOne {
2       @Override
3       public Class<? extends Annotation> annotationType() {
4           return AnotherOne.class;
5       }
6   
7       @Override
8       public boolean equals(Object o) {
9           return o instanceof AnotherOne;
10      }
11  }
```

实现，找到唯一会创建 DependencyNotFoundException 的地方是 ContextConfig 中的 checkDependencies 方法，修改为：

![image-20240819190900039](~/assets/images/spring-di/image-20240819190900039.png)

运行测试，should\_throw\_exception\_if\_dependency\_not\_found\_with\_qualifier 将通过。

但是，因为修改了返回的 DependencyNotFoundException 中的信息，所以之前创建的检查依赖缺失的测试将失败：

![image-20240819191232231](~/assets/images/spring-di/image-20240819191232231.png)

因为当前异常中的 dependency 和 component 并没有被赋值：

![Snipaste_2024-08-19_19-13-36](~/assets/images/spring-di/Snipaste_2024-08-19_19-13-36.png)

修改 DependencyNotFoundException 方法返回的信息：

![image-20240819191622688](~/assets/images/spring-di/image-20240819191622688.png)

删除未使用的字段的构造函数。

更进一步，将使用 getDependency 和 getComponent 方法的地方，替换为使用 getDependencyComponent 和 getComponentComponent：

![image-20240819191940010](~/assets/images/spring-di/image-20240819191940010.png)

至此，就没有地方使用 getDependency 和 getComponent 方法。可移除，移除后可以对 DependencyNotFoundException 中的字段和方法进行重命名。

最终，DependencyNotFoundException 重构为：

```java
1   public class DependencyNotFoundException extends RuntimeException {
2       private Component dependency;
3       private Component component;
4   
5       public DependencyNotFoundException(Component component, Component dependency) {
6           this.dependency = dependency;
7           this.component = component;
8       }
9   
10      public Component getDependency() {
11          return this.dependency;
12      }
13  
14      public Component getComponent() {
15          return this.component;
16      }
17  }
```

### [](#循环依赖 "循环依赖")循环依赖

构造测试：

我们期望： A -> @AnotherOne A -> @Named A 不构成循环依赖，因为 `Qualifier + 类型` 的组合构造类型的key

```java
1   // TODO check cyclic dependencies with qualifier
2   // A -> @AnotherOne A -> @Named A
3   static class AnotherOneDependency implements Dependency {
4       @Inject
5       public AnotherOneDependency(@jakarta.inject.Named("ChosenOne") Dependency dependency) {
6       }
7   }
8   static class NotCyclicDependency implements Dependency {
9       @Inject
10      public NotCyclicDependency(@AnotherOne Dependency dependency) {
11      }
12  }
13  @Test
14  public void should_not_throw_exception_if_component_with_same_type_tagged_with_different_qualifier() {
15      Dependency instance = new Dependency() {
16      };
17      config.bind(Dependency.class, instance, new NamedLiteral("ChosenOne"));
18      config.bind(Dependency.class, AnotherOneDependency.class, new AnotherOneLiteral());
19      config.bind(Dependency.class, NotCyclicDependency.class);
20  
21      assertDoesNotThrow(() -> config.getContext());
22  }
```

这里还需要为 NamedLiteral 创建 hashCode 方法：

```java
1   record NamedLiteral(String value) implements jakarta.inject.Named {
2       @Override
3       public Class<? extends Annotation> annotationType() {
4           return jakarta.inject.Named.class;
5       }
6   
7       @Override
8       public boolean equals(Object o) {
9           if (o instanceof jakarta.inject.Named named) return value.equals(named.value());
10          return false;
11      }
12  
13      @Override
14      public int hashCode() {
15          return "value".hashCode() * 127 ^ value.hashCode();
16      }
17  }
```

hashCode 方法需要根据 Annotation 的规范创建：

> ![image-20240819195133888](~/assets/images/spring-di/image-20240819195133888.png)

运行测试，将抛出 CyclicDependenciesException

找到抛出 CyclicDependenciesException 的代码，目前只有 ContextConfig 中的 checkDependencies 方法会抛出 CyclicDependenciesException

![image-20240819195927082](~/assets/images/spring-di/image-20240819195927082.png)

原因是 visiting 栈中只包含 Class 的信息，没有 Qualifier 注解相关的信息。

那么需要把 Stack 中的类型由 Class<?> 改为 Component，并将使用 visiting 的地方都改为 Component：

![image-20240819200809441](~/assets/images/spring-di/image-20240819200809441.png)

![image-20240819200844752](~/assets/images/spring-di/image-20240819200844752.png)

运行测试，通过。

## [](#ComponentProvider-检查-Qualifier-依赖 "ComponentProvider 检查 Qualifier 依赖")ComponentProvider 检查 Qualifier 依赖

检查 getDependencies 获取依赖时，返回正确的依赖，前面已经完成了构造器注入 Qualifier 依赖的检查。还需要检查字段注入和方法注入 Qualifier 依赖时的检查。

这里先检查方法注入时的情况。

构造测试，位于 InjectionTest.MethodInjection.WithQualifier中：

```java
1   // TODO include qualifier with dependency
2   static class InjectMethod {
3       @Inject
4       void install(@Named("ChosenOne") Dependency dependency) {
5   
6       }
7   }
8   @Test
9   public void should_include_dependency_with_qualifier() {
10      InjectionProvider<InjectMethod> provider = new InjectionProvider<>(InjectMethod.class);
11  
12      assertArrayEquals(new ComponentRef[]{ComponentRef.of(Dependency.class, new NamedLiteral("ChosenOne"))},
13              provider.getDependencies().toArray(ComponentRef[]::new));
14  }
```

实现：

![image-20240819202905248](~/assets/images/spring-di/image-20240819202905248.png)

构造字段注入 Qualifier 依赖的测试：

```java
1   // TODO include qualifier with dependency
2   static class InjectField {
3       @Inject
4       @Named("ChosenOne") Dependency dependency;
5   }
6   @Test
7   public void should_include_dependency_with_qualifier() {
8       InjectionProvider<InjectField> provider = new InjectionProvider<>(InjectField.class);
9   
10      assertArrayEquals(new ComponentRef[]{ComponentRef.of(Dependency.class, new NamedLiteral("ChosenOne"))},
11              provider.getDependencies().toArray(ComponentRef[]::new));
12  }
```

实现：

![image-20240819204156897](~/assets/images/spring-di/image-20240819204156897.png)

## [](#inject-with-qualifier "inject with qualifier")inject with qualifier

实现注入被 Qualifier 标记的依赖的功能。

### [](#构造器注入被-Qualifier-标记的依赖 "构造器注入被 Qualifier 标记的依赖")构造器注入被 Qualifier 标记的依赖

通过构造函数注入的方式，注入被 Qualifier 标记的组件，构造以下测试：

```java
1   // TODO inject with qualifier
2   @Test
3   public void should_inject_dependency_with_qualifier_via_constructor() {
4       InjectionProvider<InjectConstructor> provider = new InjectionProvider<>(InjectConstructor.class);
5   
6       InjectConstructor instance = provider.get(context);
7       assertSame(dependency, instance.dependency);
8   }
9   
10  static class InjectConstructor {
11      Dependency dependency;
12      @Inject
13      public InjectConstructor(@Named("ChosenOne") Dependency dependency) {
14          this.dependency = dependency;
15      }
16  }
```

运行测试，测试会通过。

> 这是假阴性。

因为使用了测试替身，在测试替身构造的结果和生产代码都没发生改变的情况下，就不会出现错误。就会导致假阴性。

![image-20240820092043644](~/assets/images/spring-di/image-20240820092043644.png)

无法直接修改 setUp 中的行为，因为现在直接修改的话，会产生大量的错误。

需要在当前测试中，重置 sutUp 中的行为（预期），也就是重新设置测试夹具：

```java
1   @Nested
2   class WithQualifier {
3   
4       @BeforeEach
5       public void setUp() {
6           Mockito.reset(context);
7           Mockito.when(context.get(eq(ComponentRef.of(Dependency.class, new NamedLiteral("ChosenOne"))))).thenReturn(Optional.of(dependency));
8       }
9       // TODO inject with qualifier
10      @Test
11      public void should_inject_dependency_with_qualifier_via_constructor() {
12          InjectionProvider<InjectConstructor> provider = new InjectionProvider<>(InjectConstructor.class);
13  
14          InjectConstructor instance = provider.get(context);
15          assertSame(dependency, instance.dependency);
16      }
17  }
```

此时运行测试，将不通过。

原因是，使用 get 方法获取组件时，会去容器中查找组件的依赖，并赋值到组件中。但是目前去容器中查找的方法，并没有携带 Qualifier 标记的信息，只包含了类型的信息。

![image-20240820093625332](~/assets/images/spring-di/image-20240820093625332.png)

![image-20240820093829851](~/assets/images/spring-di/image-20240820093829851.png)

实现，即查找依赖时需要从容器中获取带有 qualifier

```java
1   context.get(ComponentRef.of(type, qualifier))
```

提取一个新方法，在其中获取参数的注解，并传递给 toDependency 方法。

![image-20240820100400074](~/assets/images/spring-di/image-20240820100400074.png)

因为前面实现了一个获取方法参数的注解的功能，这里提取一个方法：

```java
1   private static Annotation getQualifier(Parameter parameter) {
2           return Arrays.stream(parameter.getAnnotations()).filter(a -> a.annotationType().isAnnotationPresent(Qualifier.class))
3                   .findFirst().orElse(null);
4       }
```

运行测试，通过。

### [](#方法注入被-Qualifier-标记的依赖 "方法注入被 Qualifier 标记的依赖")方法注入被 Qualifier 标记的依赖

通过构造函数注入的方式，注入被 Qualifier 标记的组件，构造以下测试：

```java
1   @BeforeEach
2   public void setUp() {
3       Mockito.reset(context);
4       Mockito.when(context.get(eq(ComponentRef.of(Dependency.class, new NamedLiteral("ChosenOne"))))).thenReturn(Optional.of(dependency));
5   }
6   
7   // inject with qualifier
8   @Test
9   public void should_inject_dependency_with_qualifier_via_method() {
10      InjectionProvider<InjectMethod> provider = new InjectionProvider<>(InjectMethod.class);
11  
12      InjectMethod instance = provider.get(context);
13      assertSame(dependency, instance.dependency);
14  }
15  
16  static class InjectMethod {
17      Dependency dependency;
18  
19      @Inject
20      void install(@Named("ChosenOne") Dependency dependency) {
21          this.dependency = dependency;
22      }
23  }
```

运行测试，通过。因为方法注入和构造函数注入的内部实现是一样的，所以不需要修改生产代码。

### [](#字段注入被-Qualifier-标记的依赖 "字段注入被 Qualifier 标记的依赖")字段注入被 Qualifier 标记的依赖

构造测试

```java
1   @BeforeEach
2   public void setUp() {
3       Mockito.reset(context);
4       Mockito.when(context.get(eq(ComponentRef.of(Dependency.class, new NamedLiteral("ChosenOne"))))).thenReturn(Optional.of(dependency));
5   }
6   
7   @Test
8   public void should_inject_dependency_with_qualifier_via_field() {
9       InjectionProvider<InjectField> provider = new InjectionProvider<>(InjectField.class);
10  
11      InjectField instance = provider.get(context);
12      assertSame(dependency, instance.dependency);
13  }
```

同理需要修改 toDependency 的参数：

![Snipaste_2024-08-20_10-39-36](~/assets/images/spring-di/Snipaste_2024-08-20_10-39-36.png)

因为前面实现过获取 Field 中的注解的功能，这里提取一个方法。

```java
1   private static Annotation getQualifier(Field field) {
2           return Arrays.stream(field.getAnnotations()).filter(a -> a.annotationType().isAnnotationPresent(Qualifier.class))
3                   .findFirst().orElse(null);
4       }
```

### [](#非法的-Qualifier-注入 "非法的 Qualifier 注入")非法的 Qualifier 注入

非法注入的情况是指，同时使用两个 Qualifier 注解标注同一个依赖时的情况。

根据 JSR330 规范，同一个组件可以被多个 Qualifier 标记注册多个，但是依赖只能指定一个 Qualifier 注解。

#### [](#构造器非法注入 "构造器非法注入")构造器非法注入

构造测试：

```java
1   // TODO throw illegal component if illegal qualifier given to injection point
2   static class MultiQualifierInjectConstructor {
3       @Inject
4       public MultiQualifierInjectConstructor(@Named("ChosenOne") @AnotherOne Dependency dependency) {
5       }
6   }
7   @Test
8   public void should_throw_exception_if_multi_qualifier_given_to_inject_constructor() {
9       // 需要在创建时检查依赖是否合法
10      assertThrows(IllegalComponentException.class,
11              () -> new InjectionProvider<>(MultiQualifierInjectConstructor.class));
12  }
```

运行测试，不通过，即不会抛出异常，我们需要的是抛出异常。

因为当前并没有在创建 InjectionProvider 时检查依赖是否合法，也没有去校验依赖被多个 Qualifier 标注的情况，目前只取其中一个 Qualifier 注解注册。

所以需要修改检查依赖的代码，并将检查依赖的代码加入到构造 Provider 时。

修改获取依赖参数上的 Qualifier 注解，判断注解的数量：

```java
1   private static Annotation getQualifier(Parameter parameter) {
2       List<Annotation> qualifiers = Arrays.stream(parameter.getAnnotations())
3               .filter(a -> a.annotationType().isAnnotationPresent(Qualifier.class)).toList();
4       if (qualifiers.size() > 1) throw new IllegalComponentException();
5       return qualifiers.stream().findFirst().orElse(null);
6   }
```

并在构造函数中获取依赖（获取依赖时，会调用 getQualifier 方法，即会检查依赖上的 Qualifier 是否不合法）

![image-20240820111434672](~/assets/images/spring-di/image-20240820111434672.png)

运行测试，通过。

#### [](#方法非法注入 "方法非法注入")方法非法注入

构造测试：

```java
1   static class MultiQualifierInjectMethod {
2       Dependency dependency;
3       @Inject
4       public void install(@Named("ChosenOne") @AnotherOne Dependency dependency) {
5       }
6   }
7   @Test
8   public void should_throw_exception_if_multi_qualifier_given_to_inject_method() {
9       // 需要在创建时检查依赖是否合法
10      assertThrows(IllegalComponentException.class,
11              () -> new InjectionProvider<>(MultiQualifierInjectMethod.class));
12  }
```

运行测试，直接通过。因为方法注入的内部实现和构造器注入的内部实现一致，不需要修改生产代码。

#### [](#字段非法注入 "字段非法注入")字段非法注入

构造测试：

```java
1   static class MultiQualifierInjectField {
2       @Inject
3       @Named("ChosenOne") @AnotherOne Dependency dependency;
4   }
5   @Test
6   public void should_throw_exception_if_multi_qualifier_given_to_inject_field() {
7       // 需要在创建时检查依赖是否合法
8       assertThrows(IllegalComponentException.class,
9               () -> new InjectionProvider<>(MultiQualifierInjectField.class));
10  }
```

同理，也需要修改 getQualifier 方法：

```java
1   private static Annotation getQualifier(Field field) {
2       List<Annotation> qualifiers = Arrays.stream(field.getAnnotations())
3               .filter(a -> a.annotationType().isAnnotationPresent(Qualifier.class)).toList();
4       if (qualifiers.size() > 1) throw new IllegalComponentException();
5       return qualifiers.stream().findFirst().orElse(null);
6   }
```

运行测试，通过。

# [](#重构-6 "重构")重构

## [](#合并两个-getQualifier "合并两个 getQualifier")合并两个 getQualifier

我们这里目前有两个内部实现完全一样的方法，分别是：getQualifier(Field field) 、getQualifier(Parameter parameter)

因为 Field 和 Parameter 实现了共同的 AnnotatedElement 接口，可以将这两个方法合并为一个。

```java
1   private static Annotation getQualifier(AnnotatedElement parameter) {
2       List<Annotation> qualifiers = Arrays.stream(parameter.getAnnotations())
3               .filter(a -> a.annotationType().isAnnotationPresent(Qualifier.class)).toList();
4       if (qualifiers.size() > 1) throw new IllegalComponentException();
5       return qualifiers.stream().findFirst().orElse(null);
6   }
```

简化 toDependency 代码，减少调用层级

![image-20240820141337390](~/assets/images/spring-di/image-20240820141337390.png)

![image-20240820141638666](~/assets/images/spring-di/image-20240820141638666.png)

dependency 被获取了两次，属于重复

![image-20240820142512043](~/assets/images/spring-di/image-20240820142512043.png)

这是最难发现和消除的坏味道。这可能意味着我们对模型概念的封装不足。

## [](#模型封装 "模型封装")模型封装

先创建一个封装类，将注入器和依赖组合在一起。

```java
1   static record Injectable<Element extends AccessibleObject>(Element element, ComponentRef<?>[] required){
2   
3   }
```

范型继承自 AccessibleObject，因为其子类正好包含当前需要的 Constructor、Field、Method，并使用 ComponentRef 数组表示依赖。

![image-20240820143332218](~/assets/images/spring-di/image-20240820143332218.png)

### [](#封装构造器和依赖 "封装构造器和依赖")封装构造器和依赖

使用 injectableConstructor 来代替原有的 injectConstructor，同样是先新增功能再替换：

```java
1   private Constructor<T> injectConstructor;
2   private Injectable<Constructor<T>> injectableConstructor;
```

new InjectionProvider 时，同时为 injectableConstructor 赋值，需要先获取 constructor 和 构造器依赖的 dependency，获取这两数据的代码，在现有的代码里面已经存在了，直接复用就可以。

```java
1   Constructor<T> constructor = getInjectConstructor(component);
2   ComponentRef<?>[] constructorDependencies = Arrays.stream(constructor.getParameters()).map(InjectionProvider::toComponentRef)
3           .toArray(ComponentRef<?>[]::new);
4   this.injectableConstructor = new Injectable<>(constructor, constructorDependencies);
```

接着，需要找到 injectConstructor 在哪里使用，并使用 injectableConstructor 替换掉 injectConstructor。

![image-20240820145941249](~/assets/images/spring-di/image-20240820145941249.png)

并且以上 getDependencies 方法中的部分还需要替换为如下，避免重复获取依赖，可以直接从 injectableConstructor 获取：

![image-20240820150159534](~/assets/images/spring-di/image-20240820150159534.png)

同样的，newInstance 也不需要重新获取依赖，可以直接从 injectable 中获取。

在 Injectable 中增加一个方法，直接从 context 容器中查找依赖，并返回为 newInstance 所需的数组。

```java
1   static record Injectable<Element extends AccessibleObject>(Element element, ComponentRef<?>[] required){
2       Object[] toDependencies(Context context) {
3           return Arrays.stream(required).map(context::get).map(Optional::get).toArray();
4       }
5   }
```

![image-20240820151251760](~/assets/images/spring-di/image-20240820151251760.png)

修改后，可以移除 injectConstructor。

再将 injectableConstructor 重名回 injectConstructor。

### [](#封装方法注入器和依赖 "封装方法注入器和依赖")封装方法注入器和依赖

同样的，使用 injectableMethods 替换掉 injectMethods：

```java
1   private List<Injectable<Method>> injectableMethods;
2   private List<Method> injectMethods;
```

因为构造器和普通方法都是属于方法，并且因为 Constructor 和 Method 都有一个名为 Executable 的父类，所以将构造每一个 Executable 的 Injectable 的代码提取为一个方法，用于同时创建 Constructor 和 Method 的 Injectable 封装类：

```java
1   private static <Element extends Executable> Injectable<Element> getInjectable(Element method) {
2       ComponentRef<?>[] dependencies = Arrays.stream(method.getParameters()).map(InjectionProvider::toComponentRef)
3               .toArray(ComponentRef<?>[]::new);
4       return new Injectable<>(method, dependencies);
5   }
```

![image-20240820153558513](~/assets/images/spring-di/image-20240820153558513.png)

那么 injectableMethods 的赋值语句就如下所示：

```java
1   this.injectableMethods = getInjectMethods(component).stream().map(InjectionProvider::getInjectable).toList();
```

接着找到，injectMethods 在哪里被使用

> 之前的代码有一处有问题的地方，这里应该先使用 injectMethods 替换掉，不然就在 new InjectionProvider 时，重复调用了两次 getInjectMethods 方法
> 
> ![image-20240820154445155](~/assets/images/spring-di/image-20240820154445155.png)

修为为：

![image-20240820154815243](~/assets/images/spring-di/image-20240820154815243.png)

![image-20240820154941586](~/assets/images/spring-di/image-20240820154941586.png)

修改为：

![image-20240820155126273](~/assets/images/spring-di/image-20240820155126273.png)

![image-20240820160107174](~/assets/images/spring-di/image-20240820160107174.png)

修改为：

![Snipaste_2024-08-20_16-01-58](~/assets/images/spring-di/Snipaste_2024-08-20_16-01-58.png)

移除掉 injectMethods 字段

再将 injectableMethods 重命名回 injectMethods

### [](#简单重构-2 "简单重构")简单重构

先将当前的 getInjectable 方法移动到 Injectable 中，并重命名为 of，这就是一个工厂方法：

![image-20240820161115163](~/assets/images/spring-di/image-20240820161115163.png)

### [](#封装字段注入器和依赖 "封装字段注入器和依赖")封装字段注入器和依赖

使用 injectableFields 替换掉 injectFields

```java
1   private List<Injectable<Field>> injectableFields;
2   
3   private List<Field> injectFields;
```

在 Injectable 中新建一个工厂方法：

![image-20240820161528106](~/assets/images/spring-di/image-20240820161528106.png)

那么 injectableFields 的赋值语句为：

```java
1   this.injectableFields = getInjectFields(component).stream().map(Injectable::of).toList();
```

接着查找 injectFields 在哪里被使用，并修改为 injectableFields

![image-20240820161933112](~/assets/images/spring-di/image-20240820161933112.png)

![image-20240820162458834](~/assets/images/spring-di/image-20240820162458834.png)

![image-20240820162837117](~/assets/images/spring-di/image-20240820162837117.png)

更好的实现是直接从 Injectable 中获取依赖，避免计算：

![Snipaste_2024-08-20_16-32-49](~/assets/images/spring-di/Snipaste_2024-08-20_16-32-49.png)

移除 injectFields 字段，

再将 injectableFields 重命名为 injectFields

至此，dependencies 字段已无用，也可以删除，并移除掉一些不再使用的方法。

那么，InjectionProvider 的字段和构造函数就变为：

```java
1   private Injectable<Constructor<T>> injectConstructor;
2   private List<Injectable<Method>> injectMethods;
3   private List<Injectable<Field>> injectFields;
4   
5   public InjectionProvider(Class<T> component) {
6       if (Modifier.isAbstract(component.getModifiers())) throw new IllegalComponentException();
7   
8       Constructor<T> constructor = getInjectConstructor(component);
9       this.injectConstructor = Injectable.of(constructor);
10      this.injectMethods = getInjectMethods(component).stream().map(Injectable::of).toList();
11      this.injectFields = getInjectFields(component).stream().map(Injectable::of).toList();
12  
13      if (injectFields.stream().map(Injectable::element).anyMatch(f -> Modifier.isFinal(f.getModifiers())))
14          throw new IllegalComponentException();
15      if (injectMethods.stream().map(Injectable::element).anyMatch(m -> m.getTypeParameters().length != 0))
16          throw new IllegalComponentException();
17  
18  }
```

## [](#整理代码 "整理代码")整理代码

观察发现，这几个方法只会在 Injectable 中被调用，可以将这几个方法移动到 Injectable 中

```java
1   private static ComponentRef<?> toComponentRef(Field field) {
2       Annotation qualifier = getQualifier(field);
3       return ComponentRef.of(field.getGenericType(), qualifier);
4   }
5   
6   private static ComponentRef<?> toComponentRef(Parameter parameter) {
7       Annotation qualifier = getQualifier(parameter);
8       return ComponentRef.of(parameter.getParameterizedType(), qualifier);
9   }
10  
11  private static Annotation getQualifier(AnnotatedElement parameter) {
12      List<Annotation> qualifiers = Arrays.stream(parameter.getAnnotations())
13              .filter(a -> a.annotationType().isAnnotationPresent(Qualifier.class)).toList();
14      if (qualifiers.size() > 1) throw new IllegalComponentException();
15      return qualifiers.stream().findFirst().orElse(null);
16  }
```

可以使用 Move Member 的重构方式移动：

![image-20240820171152367](~/assets/images/spring-di/image-20240820171152367.png)

![image-20240820171834398](~/assets/images/spring-di/image-20240820171834398.png)

将这些表达式都提取为方法：

![image-20240820172735344](~/assets/images/spring-di/image-20240820172735344.png)

将getDependencies 方法：

```java
1   @Override
2   public List<ComponentRef<?>> getDependencies() {
3       return Stream.concat(
4                       Stream.concat(Arrays.stream(injectConstructor.required()),
5                               injectFields.stream().map(Injectable::required).flatMap(Arrays::stream)),
6                       injectMethods.stream().map(Injectable::required).flatMap(Arrays::stream))
7               .toList();
8   }
```

简化为，先拼接为 Injectable 的 Stream，再 Map

```java
1   @Override
2   public List<ComponentRef<?>> getDependencies() {
3       return Stream.concat(Stream.concat(Stream.of(injectConstructor), injectFields.stream()), injectMethods.stream())
4               .flatMap(i -> Arrays.stream(i.required)).toList();
5   }
```

# [](#测试文档化重组 "测试文档化重组")测试文档化重组

## [](#Provider-和-Qualifier-的测试 "Provider 和 Qualifier 的测试")Provider 和 Qualifier 的测试

在 ContextText.TypeBinding.WithQualifier 中增加 Provider 和 Qualifier 相关联的两个测试，用于检查

*   获取被 Qualifier 的组件的 Provider
*   获取无对应 Qualifier 标记的组件的Provider是，Provider 应为空

```java
1   @Test
2   public void should_retrieve_bind_type_as_provider() {
3       TestComponent component = new TestComponent() {
4       };
5       config.bind(TestComponent.class, component, new NamedLiteral("ChosenOne"), new AnotherOneLiteral());
6       Context context = config.getContext();
7       Optional<Provider<TestComponent>> provider =
8               context.get(new ComponentRef<Provider<TestComponent>>(new AnotherOneLiteral()) {});
9   
10      assertTrue(provider.isPresent());
11  }
12  
13  @Test
14  public void should_retrieve_empty_if_no_matched_qualifier() {
15      TestComponent component = new TestComponent() {
16      };
17      config.bind(TestComponent.class, component);
18      Context context = config.getContext();
19      Optional<Provider<TestComponent>> provider =
20              context.get(new ComponentRef<Provider<TestComponent>>(new NamedLiteral("ChosenOne")) {});
21  
22      assertTrue(provider.isEmpty());
23  }
```

需要在 ComponentRef 中增加构造方法：

```java
1   public ComponentRef(Annotation qualifier) {
2       Type type = ((ParameterizedType) (getClass().getGenericSuperclass())).getActualTypeArguments()[0];
3       init(type, qualifier);
4   }
```

## [](#Qualifier-依赖检查参数化 "Qualifier 依赖检查参数化")Qualifier 依赖检查参数化

将当前 ContextText.DependencyCheck.WithQualifier 中两个测试修改为参数化的测试：

未找到被 Qualifier 标记的依赖时，抛出依赖不存在的异常的的参数化测试：

```java
1   // dependency missing if qualifier not match
2   @ParameterizedTest
3   @MethodSource
4   public void should_throw_exception_if_dependency_with_qualifier_not_found(Class<? extends TestComponent> componentType) {
5   
6       config.bind(Dependency.class, new Dependency() {
7       });
8       config.bind(TestComponent.class, componentType, new NamedLiteral("ChosenOne"));
9   
10      DependencyNotFoundException exception =
11              assertThrows(DependencyNotFoundException.class, () -> config.getContext());
12  
13      assertEquals(new Component(TestComponent.class, new NamedLiteral("ChosenOne")), exception.getComponent());
14      assertEquals(new Component(Dependency.class, new AnotherOneLiteral()), exception.getDependency());
15  
16  }
17  public static Stream<Arguments> should_throw_exception_if_dependency_with_qualifier_not_found() {
18      return Stream.of(
19              Arguments.of(Named.of("Constructor Injection with Qualifier", DependencyCheck.WithQualifier.InjectConstructor.class)),
20              Arguments.of(Named.of("Field Injection with Qualifier", DependencyCheck.WithQualifier.InjectField.class)),
21              Arguments.of(Named.of("Method Injection with Qualifier", DependencyCheck.WithQualifier.InjectMethod.class)),
22              Arguments.of(Named.of("Provider Constructor Injection with Qualifier", DependencyCheck.WithQualifier.InjectConstructorProvider.class)),
23              Arguments.of(Named.of("Provider Field Injection with Qualifier", DependencyCheck.WithQualifier.InjectFieldProvider.class)),
24              Arguments.of(Named.of("Provider Method Injection with Qualifier", DependencyCheck.WithQualifier.InjectMethodProvider.class))
25      );
26  }
27  
28  static class InjectConstructor implements TestComponent {
29      @Inject
30      public InjectConstructor(@AnotherOne Dependency dependency) {
31      }
32  }
33  
34  static class InjectField implements TestComponent {
35      @Inject
36      @AnotherOne Dependency dependency;
37  }
38  static class InjectMethod implements TestComponent {
39      Dependency dependency;
40  
41      @Inject
42      public void install(@AnotherOne Dependency dependency) {
43          this.dependency = dependency;
44      }
45  }
46  
47  static class InjectConstructorProvider implements TestComponent {
48      @Inject
49      public InjectConstructorProvider(@AnotherOne Provider<Dependency> dependency) {
50      }
51  }
52  
53  static class InjectFieldProvider implements TestComponent {
54      @Inject
55      @AnotherOne
56      Provider<Dependency> dependency;
57  }
58  
59  static class InjectMethodProvider implements TestComponent {
60      Dependency dependency;
61  
62      @Inject
63      public void install(@AnotherOne Provider<Dependency> dependency) {
64          this.dependency = dependency.get();
65      }
66  }
```

包含 Qualifier 标注的依赖的循环依赖检查的参数化测试：

```java
1   // check cyclic dependencies with qualifier
2   // A -> @AnotherOne A -> @Named A
3   @ParameterizedTest(name = "{1} -> @AnotherOne({0}) -> @Named(\"ChosenOne\") not cyclic dependencies")
4   @MethodSource
5   public void should_not_throw_exception_if_component_with_same_type_tagged_with_different_qualifier(Class<? extends Dependency> anotherDependencyType,
6                                                                                                  Class<? extends Dependency> notCyclicDependencyType) {
7       Dependency instance = new Dependency() {
8       };
9       config.bind(Dependency.class, instance, new NamedLiteral("ChosenOne"));
10      config.bind(Dependency.class, anotherDependencyType, new AnotherOneLiteral());
11      config.bind(Dependency.class, notCyclicDependencyType);
12  
13      assertDoesNotThrow(() -> config.getContext());
14  }
15  
16  public static Stream<Arguments> should_not_throw_exception_if_component_with_same_type_tagged_with_different_qualifier() {
17      List<Arguments> arguments = new ArrayList<>();
18      for (Named anotherDependency : List.of(Named.of("Constructor Injection", AnotherOneDependencyConstructor.class),
19              Named.of("Field Injection", DependencyCheck.WithQualifier.AnotherOneDependencyField.class),
20              Named.of("Method Injection", DependencyCheck.WithQualifier.AnotherOneDependencyMethod.class))) {
21          for (Named notCyclicDependency : List.of(Named.of("Constructor Injection", NotCyclicDependencyConstructor.class),
22                  Named.of("Field Injection", DependencyCheck.WithQualifier.NotCyclicDependencyField.class),
23                  Named.of("Method Injection", DependencyCheck.WithQualifier.NotCyclicDependencyMethod.class))) {
24              arguments.add(Arguments.of(anotherDependency, notCyclicDependency));
25          }
26      }
27      return arguments.stream();
28  }
29  
30  static class AnotherOneDependencyConstructor implements Dependency {
31      @Inject
32      public AnotherOneDependencyConstructor(@jakarta.inject.Named("ChosenOne") Dependency dependency) {
33      }
34  }
35  static class AnotherOneDependencyField implements Dependency {
36      @Inject
37      @jakarta.inject.Named("ChosenOne") Dependency dependency;
38  
39  }
40  static class AnotherOneDependencyMethod implements Dependency {
41      @Inject
42      public void install(@jakarta.inject.Named("ChosenOne") Dependency dependency) {
43      }
44  }
45  
46  static class NotCyclicDependencyConstructor implements Dependency {
47      @Inject
48      public NotCyclicDependencyConstructor(@AnotherOne Dependency dependency) {
49      }
50  }
51  static class NotCyclicDependencyField implements Dependency {
52      @Inject
53      @AnotherOne Dependency dependency;
54  }
55  static class NotCyclicDependencyMethod implements Dependency {
56      @Inject
57      public void install(@AnotherOne Dependency dependency) {
58      }
59  }
```

# [](#Singleton-生命周期管理 "Singleton-生命周期管理")Singleton-生命周期管理

Singleton 生命周期

*   注册组件时，可额外指定是否为 Singleton
*   注册组件时，可从类对象上提取 Singleton 标注
*   对于包含 Singleton 标注的组件，在容器范围内提供唯一实例
*   容器组件默认不是 Single 生命周期

基于当前的架构现状，可以将任务转换为如下 todo list

```java
1   // TODO default scope should not be singleton
2   // TODO bind component as singleton scoped
3   // TODO bind component with qualifiers as singleton scoped
4   // TODO get scope from component class
5   // TODO get scope from component with qualifiers
6   // TODO bind component with customize scope annotation
```

将任务放置在 ContextText.TypeBinding.WithScope 中：

![image-20240820192553665](~/assets/images/spring-di/image-20240820192553665.png)

## [](#默认非单例 "默认非单例")默认非单例

默认非单例模式，目前默认就是非单例模式：

```java
1   static class NotSingletonComponent {
2   }
3   @Test
4   public void should_not_be_singleton_scope_by_default() {
5       config.bind(NotSingletonComponent.class, NotSingletonComponent.class);
6       Context context = config.getContext();
7   
8       NotSingletonComponent component1 = context.get(ComponentRef.of(NotSingletonComponent.class)).get();
9       NotSingletonComponent component2 = context.get(ComponentRef.of(NotSingletonComponent.class)).get();
10  
11      assertNotSame(component1, component2);
12  }
```

被 Qualifier 标注的依赖，默认也是非单例的，在 WithScope 中再创建一个 WithQualifier 分组，测试带有 Qualifier 标注的依赖：

```java
1   @Nested
2   public class WithQualifier {
3       @Test
4       public void should_not_be_singleton_scope_by_default() {
5           config.bind(NotSingletonComponent.class, NotSingletonComponent.class, new AnotherOneLiteral());
6           Context context = config.getContext();
7   
8           NotSingletonComponent component1 = context.get(ComponentRef.of(NotSingletonComponent.class, new AnotherOneLiteral())).get();
9           NotSingletonComponent component2 = context.get(ComponentRef.of(NotSingletonComponent.class, new AnotherOneLiteral())).get();
10  
11          assertNotSame(component1, component2);
12      }
13  }
```

## [](#绑定组件为单例模式 "绑定组件为单例模式")绑定组件为单例模式

### [](#构建测试 "构建测试")构建测试

新建一个 SingletonLiteral，用于作为 bind 的参数，来指定将当前组件注册为单例模式：

```java
1   record SingletonLiteral() implements jakarta.inject.Singleton {
2       @Override
3       public Class<? extends Annotation> annotationType() {
4           return jakarta.inject.Singleton.class;
5       }
6   }
```

构造测试：

```java
1   // TODO bind component as singleton scoped
2   static class SingletonComponent {
3   }
4   @Test
5   public void should_bind_component_as_singleton_scope() {
6       config.bind(SingletonComponent.class, SingletonComponent.class, new SingletonLiteral());
7       Context context = config.getContext();
8   
9       SingletonComponent component1 = context.get(ComponentRef.of(SingletonComponent.class)).get();
10      SingletonComponent component2 = context.get(ComponentRef.of(SingletonComponent.class)).get();
11  
12      assertSame(component1, component2);
13  }
```

运行测试，会抛出一个 IllegalComponentException，抛出的位置是：

![image-20240820194638100](~/assets/images/spring-di/image-20240820194638100.png)

异常的原因是目前只支持 Qualifier 注解。

修改，让其同时支持 Qualifier 和 Scope 两种注解：

![image-20240820195127187](~/assets/images/spring-di/image-20240820195127187.png)

运行测试，现在还是异常：

```java
1   java.util.NoSuchElementException: No value present
```

不符合我们预期的 assertSame 的情况。我们预期要么相等要么不相等，不应该是不存在的情况。

原因依然在 bind 方法处，这里将 Scope 注解也当成了 Qualifier ：

![Snipaste_2024-08-20_19-55-36](~/assets/images/spring-di/Snipaste_2024-08-20_19-55-36.png)

修改，过滤掉非 Qualifier 的注解，并注意当 qualifiers 为空时也需要注册：

![image-20240820200136437](~/assets/images/spring-di/image-20240820200136437.png)

运行测试，异常，现在是我们期望的 Same 或 NotSame 异常：

```plaintext
1   Expected :world.nobug.tdd.di.ContextTest$TypeBinding$WithScope$SingletonComponent@10b892d5
2   Actual   :world.nobug.tdd.di.ContextTest$TypeBinding$WithScope$SingletonComponent@3d3f761a
```

说明目前还是非单例的。

### [](#实现-4 "实现")实现

使用一个 Proxy 或者 Decorator Pattern，包装 InjectionProvider 修改其创建行为，根据条件创建。

新建一个 ComponentProvider 的子类，其中缓存一个实例，每次 get 实例时先从缓存中取，缓存缺失时才新建：

```java
1   static class SingletonProvider<T> implements ComponentProvider<T> {
2       T instance;
3       ComponentProvider<T> provider;
4   
5       SingletonProvider(ComponentProvider<T> provider) {
6           this.provider = provider;
7       }
8   
9       @Override
10      public T get(Context context) {
11          if (instance == null) instance = provider.get(context);
12          return instance;
13      }
14  }
```

![image-20240820201833198](~/assets/images/spring-di/image-20240820201833198-1724156314344-16.png)

判断，当 Scope 存在时，使用 SingletonProvider 代替 InjectionProvider。

运行测试，通过。

同样的，构造测试，检查被 Scope 和 Qualifier 注解同时标记的依赖是否支持单例：

```java
1   // bind component with qualifiers as singleton scoped
2   @Test
3   public void should_bind_component_as_singleton_scope() {
4       config.bind(SingletonComponent.class, SingletonComponent.class, new SingletonLiteral(), new AnotherOneLiteral());
5       Context context = config.getContext();
6   
7       SingletonComponent component1 = context.get(ComponentRef.of(SingletonComponent.class, new AnotherOneLiteral())).get();
8       SingletonComponent component2 = context.get(ComponentRef.of(SingletonComponent.class, new AnotherOneLiteral())).get();
9   
10      assertSame(component1, component2);
11  }
```

运行测试，通过。

## [](#支持-Singleton "支持 @Singleton")支持 @Singleton

如果一个类被 `@Singleton` 标记，那么在绑定时可以不指定 Scope，对于这样的类默认为单例模式。

> 这个是 JSR330 规范中的一个用例，查看 Scope 注解的注释：
> 
> ![Snipaste_2024-08-20_20-37-35](~/assets/images/spring-di/Snipaste_2024-08-20_20-37-35.png)

```java
1   @Singleton
2   static class SingletonComponentAnnotated {
3   
4   }
```

### [](#构造测试-12 "构造测试")构造测试

```java
1   // TODO get scope from component class
2   @Test
3   public void should_retrieve_scope_annotation_from_component() {
4       // 未指定 scope 时，默认将标记了 Singleton 的类作为单例
5       config.bind(SingletonComponentAnnotated.class, SingletonComponentAnnotated.class);
6       Context context = config.getContext();
7   
8       SingletonComponentAnnotated component1 = context.get(ComponentRef.of(SingletonComponentAnnotated.class)).get();
9       SingletonComponentAnnotated component2 = context.get(ComponentRef.of(SingletonComponentAnnotated.class)).get();
10  
11      assertSame(component1, component2);
12  }
```

运行测试，异常：

```plaintext
1   Expected :world.nobug.tdd.di.ContextTest$TypeBinding$WithScope$SingletonComponentAnnotated@3a4b0e5d
2   Actual   :world.nobug.tdd.di.ContextTest$TypeBinding$WithScope$SingletonComponentAnnotated@10b892d5
```

### [](#实现-5 "实现")实现

目前使用的 bind 方法是：

![image-20240820204448777](~/assets/images/spring-di/image-20240820204448777.png)

修改为：

![image-20240820204544810](~/assets/images/spring-di/image-20240820204544810.png)

因为，重载的 bind 方法中现在已经支持 `Annotation... annotations` 参数为空的情况了。

同样的，构造组件同时被 Qualifier 标注时的测试：

```java
1   // TODO get scope from component with qualifiers
2   @Test
3   public void should_retrieve_scope_annotation_from_component() {
4       // 未指定 scope 时，默认将标记了 Singleton 的类作为单例
5       config.bind(SingletonComponentAnnotated.class, SingletonComponentAnnotated.class, new AnotherOneLiteral());
6       Context context = config.getContext();
7   
8       SingletonComponentAnnotated component1 = context.get(ComponentRef.of(SingletonComponentAnnotated.class, new AnotherOneLiteral())).get();
9       SingletonComponentAnnotated component2 = context.get(ComponentRef.of(SingletonComponentAnnotated.class, new AnotherOneLiteral())).get();
10  
11      assertSame(component1, component2);
12  }
```

运行测试，异常：

```plaintext
1   Expected :world.nobug.tdd.di.ContextTest$TypeBinding$WithScope$SingletonComponentAnnotated@2ddc8ecb
2   Actual   :world.nobug.tdd.di.ContextTest$TypeBinding$WithScope$SingletonComponentAnnotated@229d10bd
```

原因是目前并没有取组件上标记的 `@Singleton` , 只取了 bind 方法参数中的 Scope 注解：

![image-20240820205249652](~/assets/images/spring-di/image-20240820205249652.png)

增加从组件上获取 Scope 注解的实现，当无法从参数中获取到 Scope 时，尝试将 scope 赋值为从组件上获取到的 Scope 注解：

![Snipaste_2024-08-20_20-59-15](~/assets/images/spring-di/Snipaste_2024-08-20_20-59-15.png)

运行测试，通过。

## [](#小-bug "小 bug")小 bug

![image-20240820210355336](~/assets/images/spring-di/image-20240820210355336.png)

这里不应该从 type 取注解，而是应该从 implementation 上取。

## [](#依赖检查-1 "依赖检查")依赖检查

### [](#依赖不存在 "依赖不存在")依赖不存在

```java
1   // dependencies not exist
2   @ParameterizedTest
3   @MethodSource
4   public void should_throw_exception_if_dependency_not_found(Class<? extends TestComponent> componentType) {
5       config.bind(TestComponent.class, componentType);
6   
7       DependencyNotFoundException exception = assertThrows(DependencyNotFoundException.class, () -> {
8           config.getContext();
9       });
10  
11      assertEquals(Dependency.class, exception.getDependency().type());
12      assertEquals(TestComponent.class, exception.getComponent().type());
13  }
```

增加一个被 @Singleton 标记的测试用例：

![image-20240821093308594](~/assets/images/spring-di/image-20240821093308594.png)

```java
1   @Singleton
2   static class MissingDependencyScope implements TestComponent {
3       @Inject
4       Dependency dependency;
5   }
```

运行测试：

```plaintext
1   org.opentest4j.AssertionFailedError: Expected world.nobug.tdd.di.DependencyNotFoundException to be thrown, but nothing was thrown.
```

我们预期应该抛出依赖不存在的异常，但是这里并没有抛出。说明在 config.getContext() 中 checkDependencies 时并没有获取到该组件的正确依赖。因为当前组件被构建成 SingletonProvider 并且当前并没有实现 getDependencies 方法，实现该方法：

```java
1   static class SingletonProvider<T> implements ComponentProvider<T> {
2       T instance;
3       ComponentProvider<T> provider;
4   
5       SingletonProvider(ComponentProvider<T> provider) {
6           this.provider = provider;
7       }
8   
9       @Override
10      public T get(Context context) {
11          if (instance == null) {
12              instance = provider.get(context);
13          }
14          return instance;
15      }
16  
17      @Override
18      public List<ComponentRef<?>> getDependencies() {
19          return provider.getDependencies();
20      }
21  }
```

运行测试，通过。

再增加一个 Provider包装的依赖的测试：

```java
1   Arguments.of(Named.of("Provider Scope", DependencyCheck.MissingDependencyProviderScope.class))
```

```java
1   @Singleton
2   static class MissingDependencyProviderScope implements TestComponent {
3       @Inject
4       Provider<Dependency> dependency;
5   }
```

运行测试，通过。

### [](#循环依赖-1 "循环依赖")循环依赖

对于 Scope 的循环依赖是一个可选项。

这种情况有一个很典型的优化：当两个组件都是构造函数相互依赖时，并且其中有一个是 Singleton 的，那么这个循环依赖是不成立的，因为并不是每次都需要构造新对象。

## [](#自定义-Scope-注解 "自定义 Scope 注解")自定义 Scope 注解

自定义一个 Scope 注解 Pooled，来表示指定数量的多例：

```java
1   @Scope
2   @Documented
3   @Retention(RUNTIME)
4   @interface Pooled {}
5   
6   record PooledLiteral() implements Pooled {
7       @Override
8       public Class<? extends Annotation> annotationType() {
9           return Pooled.class;
10      }
11  }
```

同样的，需要定义一个 Provider：

```java
1   class PooledProvider<T> implements ContextConfig.ComponentProvider<T> {
2       static int MAX = 2;
3   
4       private int current;
5       private List<T> instancePool = new ArrayList<>();
6       ContextConfig.ComponentProvider<T> provider;
7   
8       PooledProvider(ContextConfig.ComponentProvider<T> provider) {
9           this.provider = provider;
10      }
11  
12      @Override
13      public T get(Context context) {
14          if (instancePool.size() < MAX) instancePool.add(provider.get(context));
15          return instancePool.get(current++ % MAX);
16      }
17  
18      @Override
19      public List<ComponentRef<?>> getDependencies() {
20          return provider.getDependencies();
21      }
22  }
```

### [](#构造测试-13 "构造测试")构造测试

```java
1   // TODO bind component with customize scope annotation
2   static class PooledComponent {
3   
4   }
5   @Test
6   public void should_bind_component_with_customize_scope_annotation() {
7       config.bind(PooledComponent.class, PooledComponent.class, new PooledLiteral());
8       Context context = config.getContext();
9   
10      List<PooledComponent> instances = IntStream.range(0, 5)
11              .mapToObj(i -> context.get(ComponentRef.of(PooledComponent.class)).get()).toList();
12      assertEquals(PooledProvider.MAX, new HashSet<>(instances).size());
13  }
```

运行测试，将失败：

```plaintext
1   Expected :2
2   Actual   :1
```

因为我们当前将所有 Scope 的注解都设置为单例。

### [](#实现-6 "实现")实现

我们预期的方式是，为 config 配置指定的 Scope 应该如何创建对应的 Provider：

![image-20240821103932822](~/assets/images/spring-di/image-20240821103932822.png)

创建该方法：

```java
1   public <ScopeType extends Annotation> void scope(Class<ScopeType> scopeType, Function<ComponentProvider<?>, ComponentProvider<?>> provider) {
2   }
```

新建一个字段来保存 scope 信息：

```java
1   private Map<Class<?>, Function<ComponentProvider<?>, ComponentProvider<?>>> scopes = new HashMap<>();
```

那么 scope 方法的实现为：

```java
1   public <ScopeType extends Annotation> void scope(Class<ScopeType> scopeType, Function<ComponentProvider<?>, ComponentProvider<?>> provider) {
2       scopes.put(scopeType, provider);
3   }
```

然后还需要新建一个默认构造函数，并在其中初始化默认的 Scope 的 Provider 方法：

```java
1   public ContextConfig() {
2       scopes.put(Singleton.class, SingletonProvider::new);
3   }
```

修改 bind 方法中获取 scope 的 provider 的实现：

```java
1   if (scope.isPresent()) provider = scopes.get(scope.get().annotationType()).apply(provider);
```

运行测试，通过。

## [](#重构-7 "重构")重构

重构之前，先将 ComponentProvider 和 SingletonProvider 移动到最外层。

为下面的参数定义一个函数式接口，简化代码：

![Snipaste_2024-08-21_11-10-20](~/assets/images/spring-di/Snipaste_2024-08-21_11-10-20.png)

![Snipaste_2024-08-21_11-13-29](~/assets/images/spring-di/Snipaste_2024-08-21_11-13-29.png)

```java
1   interface ScopeProvider {
2       ComponentProvider<?> create(ComponentProvider<?> provider);
3   }
```

对应的修改后：

![image-20240821111855275](~/assets/images/spring-di/image-20240821111855275.png)

![image-20240821111943949](~/assets/images/spring-di/image-20240821111943949.png)

### [](#重构简化-bind-方法 "重构简化 bind 方法")重构简化 bind 方法

目前，这个 bind 方法中的实现比较复杂：

![image-20240821114336444](~/assets/images/spring-di/image-20240821114336444.png)

分析，这个代码中主要是对不同类型的 annotations 参数进行处理，目前这个参数中包含的的类型有：

*   Scope
*   Qualifier
*   其他

我们要做的就是将 annotations 根据 Scope、Qualifier 和 其他来进行分类。

这里我们可以将 “其他” 这个类别用一个自定义的注解表示：

```java
1   private @interface Illegal {
2   
3   }
```

并定义一个分类函数：

```java
1   private Class<? extends Annotation> typeOf(Annotation annotation) {
2       Class<? extends Annotation> type = annotation.annotationType();
3       return Stream.of(Qualifier.class, Scope.class)
4               .filter(type::isAnnotationPresent)
5               .findFirst()
6               .orElse(Illegal.class);
7   }
```

那么分组函数就是：

```java
1   Map<Class<?>, List<Annotation>> annotationGroups =
2           Arrays.stream(annotations).collect(Collectors.groupingBy(this::typeOf, Collectors.toList()));
```

然后通过使用分组的数据来简化后面的代码逻辑。

首先，是对 Illegal 情况的判断：

![image-20240821134009469](~/assets/images/spring-di/image-20240821134009469.png)

简化为：

```java
1   if (annotationGroups.containsKey(Illegal.class)) throw new IllegalComponentException();
```

## [](#Scope-Sad-Path "Scope Sad Path")Scope Sad Path

增加几个关于 Scope 的 sad path

```java
1   // TODO multi scope provided
2   // TODO multi scope annotated
3   // TODO undefined scope
```

注册时为组件设置多个 scope，构造测试：

```java
1   // TODO multi scope provided
2   @Test
3   public void should_throw_exception_if_multi_scope_provided() {
4       config.scope(Pooled.class, PooledProvider::new);
5       config.scope(Singleton.class, SingletonProvider::new);
6       assertThrows(IllegalComponentException.class,
7               () -> config.bind(PooledComponent.class, PooledComponent.class, new PooledLiteral(), new SingletonLiteral()));
8   }
```

运行测试，不通过。说明并没有判断设置多个 Scope 的情况。

增加判断：

![Snipaste_2024-08-21_14-20-48](~/assets/images/spring-di/Snipaste_2024-08-21_14-20-48.png)

多个 Scope 注解标注同一个组件时

```java
1   // multi scope annotated
2   @Singleton @Pooled
3   static class MultiScopeAnnotatedComponent {
4   
5   }
6   @Test
7   public void should_throw_exception_if_multi_scope_annotated() {
8       config.scope(Pooled.class, PooledProvider::new);
9       assertThrows(IllegalComponentException.class,
10              () -> config.bind(MultiScopeAnnotatedComponent.class, MultiScopeAnnotatedComponent.class));
11  }
```

运行测试，通过。

注册时，设置未定义的 Scope：

```java
1   // TODO undefined scope
2   @Test
3   public void should_throw_exception_if_undefined_scope() {
4       assertThrows(IllegalComponentException.class,
5               () -> config.bind(PooledComponent.class, PooledComponent.class, new PooledLiteral()));
6   }
```

在这个测试中并没有指定在容器中配置 Pooled 注解如何定义 Provider，也就是没有执行 `config.scope(Pooled.class, PooledProvider::new);`

运行测试，异常：

```plaintext
1   org.opentest4j.AssertionFailedError: Unexpected exception type thrown ==> expected: <world.nobug.tdd.di.IllegalComponentException> but was: <java.lang.NullPointerException>
```

有一个空指针异常，是因为无法获取 Pooled 注解对应的 Provider，获取到的为 null。

修改实现：

![image-20240821144348995](~/assets/images/spring-di/image-20240821144348995.png)

运行测试，通过。

# [](#测试覆盖率 "测试覆盖率")测试覆盖率

Run …. with Coverage 检查代码的测试覆盖率：

![image-20240821145440311](~/assets/images/spring-di/image-20240821145440311.png)

![image-20240821150535770](~/assets/images/spring-di/image-20240821150535770.png)

虽然我们没有做到 100% 的代码覆盖了，但是我们做到了 100% 的功能覆盖，对于有些行因为语言特性的需求或者其他原因的代码，也没有必要写测试覆盖。

# [](#走的更远 "走的更远")走的更远

可以引入 Jakarta 的 tck 包，来测试当前容器对 JSR330 规范的兼容度，并完善对 JSR330 规范的兼容。