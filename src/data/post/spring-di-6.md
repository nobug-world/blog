---
publishDate: 2024-08-21T02:00:00Z
title: 'TDD 实现 Spring DI 容器 (六) - Qualifier 支持'
excerpt: '本文在基础的按类型注入之上，集成了 Qualifier (限定符) 和默认 Named 注解支持，通过重构组件标识体系使其能够精准匹配同类型下的各种不同实现。'
category: 'TDD'
tags:
  - TDD
metadata:
  canonical: https://nobug.world/blogs/25729/
---
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

