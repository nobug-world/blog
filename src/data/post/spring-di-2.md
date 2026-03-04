---
publishDate: 2024-08-21T00:00:00Z
title: 'TDD 实现 Spring DI 容器 (二) - 依赖检查提取'
excerpt: '本文聚焦容器依赖构建过程中的 Sad Path 处理，详细演示了将依赖缺失与循环依赖等检查逻辑抽离至容器构建阶段，彻底重构了内部的依赖获取与上下文构建链路。'
category: 'TDD'
tags:
  - TDD
metadata:
  canonical: https://nobug.world/blogs/25729/
---
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

