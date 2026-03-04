---
publishDate: 2024-08-21T00:00:00Z
title: 'TDD 实现 Spring DI 容器 (四) - 代码与测试重构'
excerpt: '本文是一次高质量的重构实战，通过提取测试上下文、参数化测试用例来使测试文档化，进一步分离了测试代码架构，消除代码坏味道以保证容器本身及其测试用例易于维护。'
category: 'TDD'
tags:
  - TDD
metadata:
  canonical: https://nobug.world/blogs/25729/
---
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

