---
publishDate: 2024-08-21T00:00:00Z
title: 'TDD 实现 Spring DI 容器 (五) - Provider 依赖注入'
excerpt: '本文介绍了如何使用 TDD 的方式实现一个简单的 Spring DI 容器，包含注入点的支持、组件的构造、依赖的选择以及生命周期控制。'
category: 'TDD'
tags:
  - TDD
metadata:
  canonical: https://nobug.world/blogs/25729/
---
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

