---
publishDate: 2024-08-21T00:00:00Z
title: 'TDD 实现 Spring DI 容器 (七) - 生命周期管理'
excerpt: '本文介绍了如何使用 TDD 的方式实现一个简单的 Spring DI 容器，包含注入点的支持、组件的构造、依赖的选择以及生命周期控制。'
category: 'TDD'
tags:
  - TDD
metadata:
  canonical: https://nobug.world/blogs/25729/
---
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