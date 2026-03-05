---
publishDate: 2024-08-21T07:00:00Z
title: 'TDD 实现 Spring DI 容器 (一) - 基础功能与实例构造'
excerpt: '本文介绍了 TDD 实现 Spring DI 容器的背景和需求分析，进行功能任务分解，并搭建测试环境，带领大家通过红绿重构循环实现基础的组件注册与实例构造机制。'
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

