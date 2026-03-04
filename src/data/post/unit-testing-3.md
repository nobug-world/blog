---
publishDate: 2024-09-10T00:00:00Z
title: '单元测试原则、实践与模式（三）'
excerpt: '本章内容涵盖单元测试的结构，单元测试命名的最佳实践，使用参数化测试和使用流畅的断言。'
category: '测试'
tags:
  - 单元测试
metadata:
  canonical: https://nobug.world/blogs/48316/
---

> 译者声明：本译文仅作为学习的记录，不作为任务商业用途，如有侵权请告知我删除。  
> **本文禁止转载！**  
> 请支持原书正版：[https://www.manning.com/books/unit-testing](https://www.manning.com/books/unit-testing)


# [](#第三章-剖析单元测试 "第三章 剖析单元测试")第三章 剖析单元测试

**Chapter 3 The anatomy of a unit test**

This chapter covers 本章内容涵盖

*   The structure of a unit test 单元测试的结构
*   Unit test naming best practices 单元测试命名的最佳实践
*   Working with parameterized tests 使用参数化测试
*   Working with fluent assertions 使用流畅的断言

In this remaining chapter of part 1, I’ll give you a refresher on some basic topics. I’ll go over the structure of a typical unit test, which is usually represented by the arrange, act, and assert (AAA) pattern. I’ll also show the unit testing framework of my choice—xUnit—and explain why I’m using it and not one of its competitors.

在第一部分剩下的这一章中，我将给你一个关于一些基本主题的复习。我将介绍一个典型的单元测试的结构，它通常由准备、执行和断言（AAA）模式表示。我还将展示我选择的单元测试框架–xUnit，并解释为什么我使用它而不是它的竞争对手。

Along the way, we’ll talk about naming unit tests. There are quite a few competing pieces of advice on this topic, and unfortunately, most of them don’t do a good enough job improving your unit tests. In this chapter, I describe those less-useful naming practices and show why they usually aren’t the best choice. Instead of those practices, I give you an alternative—a simple, easy-to-follow guideline for naming tests in a way that makes them readable not only to the programmer who wrote them, but also to any other person familiar with the problem domain.

在此过程中，我们将讨论单元测试的命名问题。在这个问题上有不少相互竞争的建议，不幸的是，它们中的大多数都没有很好地改善你的单元测试。在这一章中，我描述了那些不太有用的命名方法，并说明为什么它们通常不是最佳选择。我给你一个取代这些做法的替代方案–一个简单易行的准则，用于命名测试，使其不仅对编写测试的程序员，而且对任何其他熟悉问题领域的人都具有可读性。

Finally, I’ll talk about some features of the framework that help streamline the process of unit testing. Don’t worry about this information being too specific to C# and .NET; most unit testing frameworks exhibit similar functionality, regardless of the programming language. If you learn one of them, you won’t have problems working with another.

最后，我将谈谈该框架的一些特点，这些特点有助于简化单元测试的过程。不要担心这些信息对 C# 和 .NET 过于特殊，大多数单元测试框架都表现出类似的功能，不管是哪种编程语言。如果你学会了其中一种，你在使用另一种时就不会有问题。

## [](#3-1-如何构造单元测试 "3.1 如何构造单元测试")3.1 如何构造单元测试

**How to structure a unit test**

This section shows how to structure unit tests using the arrange, act, and assert pattern, what pitfalls to avoid, and how to make your tests as readable as possible.

这一节展示了如何使用准备、执行和断言模式来组织单元测试，避免哪些陷阱，以及如何使你的测试尽可能的可读。

### [](#3-1-1-使用-AAA-模式 "3.1.1 使用 AAA 模式")3.1.1 使用 AAA 模式

**Using the AAA pattern**

The AAA pattern advocates for splitting each test into three parts: arrange, act, and assert. (This pattern is sometimes also called the 3A pattern.) Let’s take a Calculator class with a single method that calculates a sum of two numbers:

AAA 模式主张将每个测试分成三个部分：准备，执行，和断言。(这种模式有时也被称为 3A 模式。) 让我们来看看一个计算器类，它有一个计算两个数字之和的单一方法：

```csharp
1   public class Calculator
2   {
3   	public double Sum(double first, double second)
4   	{
5   		return first + second;
6   	}
7   }
```

The following listing shows a test that verifies the class’s behavior. This test follows the AAA pattern.

下面的列表显示了一个验证该类行为的测试。这个测试遵循 AAA 模式。

Listing 3.1 A test covering the Sum method in calculator

![image-20230409203257221](~/assets/images/unit-testing-3/image-20230409203257221.png)

The AAA pattern provides a simple, uniform structure for all tests in the suite. This uniformity is one of the biggest advantages of this pattern: once you get used to it, you can easily read and understand any test. That, in turn, reduces maintenance costs for your entire test suite. The structure is as follows:

AAA 模式为套件中的所有测试提供了一个简单、统一的结构。这种统一性是这种模式的最大优势之一：一旦你习惯了它，你就可以很容易地阅读和理解任何测试。这反过来又降低了你整个测试套件的维护成本。其结构如下：

*   In the arrange section, you bring the system under test (SUT) and its dependencies to a desired state. 在准备部分，你把被测系统（SUT）和它的依赖置于所需状态。
*   In the act section, you call methods on the SUT, pass the prepared dependencies, and capture the output value (if any). 在执行部分，你调用 SUT 的方法，传递准备好的依赖，并捕获输出值（如果有的话）。
*   In the assert section, you verify the outcome. The outcome may be represented by the return value, the final state of the SUT and its collaborators, or the methods the SUT called on those collaborators. 在断言部分，你要验证结果。结果可以由返回值、SUT 及其合作者的最终状态或 SUT 对这些合作者调用的方法来表示。

> **Given-When-Then pattern**
> 
> You might have heard of the Given-When-Then pattern, which is similar to AAA. This pattern also advocates for breaking the test down into three parts:
> 
> 你可能听说过 Given-When-Then 模式，它与 AAA 模式类似。这种模式也主张将测试分解成三个部分：
> 
> *   Given—Corresponds to the arrange section 对应于准备部分
> *   When—Corresponds to the act section 对应于执行部分
> *   Then—Corresponds to the assert section 对应于断言部分
> 
> There’s no difference between the two patterns in terms of the test composition. The only distinction is that the Given-When-Then structure is more readable to nonprogrammers. Thus, Given-When-Then is more suitable for tests that are shared with non-technical people.
> 
> 这两种模式在测试构成上没有区别。唯一的区别是 Given-When-Then 结构对非程序员来说更容易阅读。因此，Given-When-Then 更适合于与非技术人员共享的测试。

The natural inclination is to start writing a test with the arrange section. After all, it comes before the other two. This approach works well in the vast majority of cases, but starting with the assert section is a viable option too. When you practice Test-Driven Development (TDD)—that is, when you create a failing test before developing a feature—you don’t know enough about the feature’s behavior yet. So, it becomes advantageous to first outline what you expect from the behavior and then figure out how to develop the system to meet this expectation.

人们自然倾向于从准备部分开始编写测试。毕竟，它是在其他两个部分之前。这种方法在绝大多数情况下都很有效，但从断言部分开始也是一个可行的选择。当你实践测试驱动开发（TDD）时–也就是说，当你在开发一个功能之前创建一个失败的测试时，你对这个功能的行为还没有足够的了解。因此，首先勾勒出你对行为的期望，然后想出如何开发系统来满足这一期望，这就变得很有利。

Such a technique may look counterintuitive, but it’s how we approach problem solving. We start by thinking about the objective: what a particular behavior should to do for us. The actual solving of the problem comes after that. Writing down the assertions before everything else is merely a formalization of this thinking process. But again, this guideline is only applicable when you follow TDD—when you write a test before the production code. If you write the production code before the test, by the time you move on to the test, you already know what to expect from the behavior, so starting with the arrange section is a better option.

这样的技术可能看起来有悖常理，但这就是我们解决问题的方式。我们从思考目标开始：一个特定的行为应该为我们做什么。之后才是解决问题的实际过程。在其他事情之前写下断言，只是这种思考过程的形式化。但同样的，这个准则只适用于当你遵循 TDD 时–当你在生产代码之前写下测试时。如果你在测试之前写生产代码，当你转到测试的时候，你已经知道对行为的期望，所以从准备部分开始是一个更好的选择。

### [](#3-1-2-避免多个准备、执行和断言部分 "3.1.2 避免多个准备、执行和断言部分")3.1.2 避免多个准备、执行和断言部分

**Avoid multiple arrange, act, and assert sections**

Occasionally, you may encounter a test with multiple arrange, act, or assert sections. It usually works as shown in figure 3.1.

偶尔，你可能会遇到一个有多个准备, 执行, 或断言部分的测试。它的工作原理通常如图3.1所示。

![image-20230409203506161](~/assets/images/unit-testing-3/image-20230409203506161.png)

Figure 3.1 Multiple arrange, act, and assert sections are a hint that the test verifies too many things at once. Such a test needs to be split into several tests to fix the problem. 图 3.1 多个准备, 执行, 和断言部分是一个提示，说明测试一次验证了太多的东西。这样的测试需要拆分成几个测试来解决这个问题。

When you see multiple act sections separated by assert and, possibly, arrange sections, it means the test verifies multiple units of behavior. And, as we discussed in chapter 2, such a test is no longer a unit test but rather is an integration test. It’s best to avoid such a test structure. A single action ensures that your tests remain within the realm of unit testing, which means they are simple, fast, and easy to understand. If you see a test containing a sequence of actions and assertions, refactor it. Extract each act into a test of its own.

当你看到多个执行部分被断言和可能的准备部分隔开时，这意味着测试验证了多个行为单元。而且，正如我们在第二章所讨论的，这样的测试不再是一个单元测试，而是一个集成测试。最好的办法是避免这样的测试结构。单一的执行可以确保你的测试保持在单元测试的范围内，这意味着它们是简单、快速和容易理解的。如果你看到一个包含一连串执行和断言的测试，请重构它。将每个行为提取为一个独立的测试。

It’s sometimes fine to have multiple act sections in integration tests. As you may remember from the previous chapter, integration tests can be slow. One way to speed them up is to group several integration tests together into a single test with multiple acts and assertions. It’s especially helpful when system states naturally flow from one another: that is, when an act simultaneously serves as an arrange for the subsequent act.

有时，在集成测试中有多个执行部分是可以的。你可能还记得前一章的内容，集成测试可能很慢。加快速度的方法之一是将几个集成测试组合成一个具有多个执行和断言的单一测试。当系统状态自然地相互流动时，这尤其有帮助：也就是说，当一个行为同时作为后续行为的执行时。

But again, this optimization technique is only applicable to integration tests—and not all of them, but rather those that are already slow and that you don’t want to become even slower. There’s no need for such an optimization in unit tests or integration tests that are fast enough. It’s always better to split a multistep unit test into several tests.

但同样，这种优化技术只适用于集成测试，而且不是所有的集成测试，而是那些已经很慢的测试，你不希望变得更慢。在足够快的单元测试或集成测试中，没有必要进行这样的优化。把一个多步骤的单元测试分成几个测试总是更好的。

### [](#3-1-3-避免在测试中使用-if-语句 "3.1.3 避免在测试中使用 if 语句")3.1.3 避免在测试中使用 if 语句

**Avoid if statements in tests**

Similar to multiple occurrences of the arrange, act, and assert sections, you may sometimes encounter a unit test with an if statement. This is also an anti-pattern. A test— whether a unit test or an integration test—should be a simple sequence of steps with no branching.

与准备、执行和断言部分的多次出现类似，有时你可能会遇到一个带有 if 语句的单元测试。这也是一种反模式。一个测试–无论是单元测试还是集成测试–应该是一个简单的步骤序列，没有分支。

An if statement indicates that the test verifies too many things at once. Such a test, therefore, should be split into several tests. But unlike the situation with multiple AAA sections, there’s no exception for integration tests. There are no benefits in branching within a test. You only gain additional maintenance costs: if statements make the tests harder to read and understand.

一个 if 语句表明该测试同时验证了太多的东西。因此，这样的测试应该被分割成几个测试。但与多个 AAA 部分的情况不同，集成测试也没有例外。在一个测试中进行分支，没有任何好处。你只能获得额外的维护成本：if 语句使测试更难阅读和理解。

### [](#3-1-4-每个部分应该有多大 "3.1.4 每个部分应该有多大?")3.1.4 每个部分应该有多大?

**How large should each section be?**

A common question people ask when starting out with the AAA pattern is, how large should each section be? And what about the teardown section—the section that cleans up after the test? There are different guidelines regarding the size for each of the test sections.

在开始使用 AAA 模式时，人们常问的一个问题是，每个部分应该有多大？那么复原部分–测试后的清理部分呢？关于每个测试部分的尺寸，有不同的准则。

> THE ARRANGE SECTION IS THE LARGEST 准备部分是最大的
> 
> The arrange section is usually the largest of the three. It can be as large as the act and assert sections combined. But if it becomes significantly larger than that, it’s better to extract the arrangements either into private methods within the same test class or to a separate factory class. Two popular patterns can help you reuse the code in the arrange sections: Object Mother and Test Data Builder.
> 
> 准备部分通常是三个部分中最大的一个。它可以和执行和断言部分的总和一样大。但如果它变得比这大得多，最好是将准备提取到同一个测试类中的私有方法中，或者提取到一个单独的工厂类中。两个流行的模式可以帮助你重用准备部分的代码： Object Mother 和 Test Data Builder。

> WATCH OUT FOR ACT SECTIONS THAT ARE LARGER THAN A SINGLE LINE 注意那些大于一行的执行部分
> 
> The act section is normally just a single line of code. If the act consists of two or more lines, it could indicate a problem with the SUT’s public API.
> 
> 执行部分通常只有一行代码。如果执行由两行或多行组成，这可能表明 SUT 的公共 API 有问题。
> 
> It’s best to express this point with an example, so let’s take one from chapter 2, which I repeat in the following listing. In this example, the customer makes a purchase from a store.
> 
> 最好用一个例子来表达这一点，所以让我们拿第二章中的一个例子，我在下面的列表中重复了这个例子。在这个例子中，客户从一家商店购买了东西。

Listing 3.2 A single-line act section

```csharp
1   [Fact]
2   public void Purchase_succeeds_when_enough_inventory()
3   {
4   	// Arrange
5   	var store = new Store();
6   	store.AddInventory(Product.Shampoo, 10);
7   	var customer = new Customer();
8   	// Act
9   	bool success = customer.Purchase(store, Product.Shampoo, 5);
10  	// Assert
11  	Assert.True(success);
12  	Assert.Equal(5, store.GetInventory(Product.Shampoo));
13  }
```

Notice that the act section in this test is a single method call, which is a sign of a welldesigned class’s API. Now compare it to the version in listing 3.3: this act section contains two lines. And that’s a sign of a problem with the SUT: it requires the client to remember to make the second method call to finish the purchase and thus lacks encapsulation.

请注意，这个测试中的执行部分是一个单一的方法调用，这是一个设计良好的类的 API 的标志。现在将其与列表 3.3 中的版本进行比较：这个执行部分包含两行。这说明 SUT 有问题：它要求客户记住进行第二次方法调用来完成购买，因此缺乏封装。

Listing 3.3 A two-line act section

```csharp
1   [Fact]
2   public void Purchase_succeeds_when_enough_inventory()
3   {
4   	// Arrange
5   	var store = new Store();
6   	store.AddInventory(Product.Shampoo, 10);
7   	var customer = new Customer();
8   	// Act
9   	bool success = customer.Purchase(store, Product.Shampoo, 5);
10  	store.RemoveInventory(success, Product.Shampoo, 5);
11  	// Assert
12  	Assert.True(success);
13  	Assert.Equal(5, store.GetInventory(Product.Shampoo));
14  }
```

Here’s what you can read from listing 3.3’s act section:

下面是你可以从清单 3.3 的行执行部分读到的内容：

*   In the first line, the customer tries to acquire five units of shampoo from the store. 在第一行中，顾客试图从商店获得五个单位的洗发水。
*   In the second line, the inventory is removed from the store. The removal takes place only if the preceding call to Purchase() returns a success. 在第二行中，库存被从商店中移除。只有当前面对 Purchase() 的调用返回成功时，才会发生移除的情况。

The issue with the new version is that it requires two method calls to perform a single operation. Note that this is not an issue with the test itself. The test still verifies the same unit of behavior: the process of making a purchase. The issue lies in the API surface of the Customer class. It shouldn’t require the client to make an additional method call.

新版本的问题是，它需要两个方法调用来执行一个操作。请注意，这不是测试本身的问题。测试仍然验证了相同的行为单元：购买的过程。问题在于客户类的 API 表面。它不应该要求客户进行额外的方法调用。

From a business perspective, a successful purchase has two outcomes: the acquisition of a product by the customer and the reduction of the inventory in the store. Both of these outcomes must be achieved together, which means there should be a single public method that does both things. Otherwise, there’s a room for inconsistency if the client code calls the first method but not the second, in which case the customer will acquire the product but its available amount won’t be reduced in the store.

从商业角度来看，一个成功的购买有两个结果：客户获得产品和减少商店里的库存。这两个结果必须同时实现，这意味着应该有一个单一的公共方法来做这两件事。否则，如果客户代码调用第一个方法而不调用第二个方法，就会出现不一致的情况，在这种情况下，客户会获得产品，但商店中的可用数量不会减少。

Such an inconsistency is called an invariant violation. The act of protecting your code against potential inconsistencies is called encapsulation. When an inconsistency penetrates into the database, it becomes a big problem: now it’s impossible to reset the state of your application by simply restarting it. You’ll have to deal with the corrupted data in the database and, potentially, contact customers and handle the situation on a case-by-case basis. Just imagine what would happen if the application generated confirmation receipts without actually reserving the inventory. It might issue claims to, and even charge for, more inventory than you could feasibly acquire in the near future.

这样的不一致被称为违反不变量。保护你的代码不受潜在的不一致影响的行为被称为封装。当一个不一致渗透到数据库中时，它就成了一个大问题：现在不可能通过简单的重启来重置你的应用程序的状态。你将不得不处理数据库中被破坏的数据，并有可能联系客户，逐一处理。试想一下，如果应用程序生成确认收据而不实际预留库存会发生什么。它可能会对更多的库存发出索赔，甚至收取费用，而这些库存是你在不久的将来可以获得的。

The remedy is to maintain code encapsulation at all times. In the previous example, the customer should remove the acquired inventory from the store as part of its Purchase method and not rely on the client code to do so. When it comes to maintaining invariants, you should eliminate any potential course of action that could lead to an invariant violation.

补救措施是在任何时候都要保持代码的封装。在前面的例子中，客户应该将获得的库存从商店中删除，作为其购买方法的一部分，而不是依赖客户代码来做。当涉及到维护不变量时，你应该消除任何可能导致违反不变量的潜在行为过程。

This guideline of keeping the act section down to a single line holds true for the vast majority of code that contains business logic, but less so for utility or infrastructure code. Thus, I won’t say “never do it.” Be sure to examine each such case for a potential breach in encapsulation, though.

这种将执行部分缩减到一行的准则对于绝大多数包含业务逻辑的代码来说都是正确的，但对于工具代码或基础设施代码来说就不那么正确了。因此，我不会说 “永远不要这样做”。不过，一定要检查每一个这样的案例是否有潜在的违反封装的情况。

### [](#3-1-5-断言部分应该包含多少个断言 "3.1.5 断言部分应该包含多少个断言?")3.1.5 断言部分应该包含多少个断言?

**How many assertions should the assert section hold?**

Finally, there’s the assert section. You may have heard about the guideline of having one assertion per test. It takes root in the premise discussed in the previous chapter: the premise of targeting the smallest piece of code possible.

最后，是断言部分。你可能听说过每个测试有一个断言的准则。它源于上一章讨论的前提：以尽可能小的代码为目标的前提。

As you already know, this premise is incorrect. A unit in unit testing is a unit of behavior, not a unit of code. A single unit of behavior can exhibit multiple outcomes, and it’s fine to evaluate them all in one test.

正如你已经知道的，这个前提是不正确的。单元测试中的单元是行为的单元，而不是代码的单元。一个行为单元可以表现出多种结果，在一个测试中对它们进行评估是可以的。

Having that said, you need to watch out for assertion sections that grow too large: it could be a sign of a missing abstraction in the production code. For example, instead of asserting all properties inside an object returned by the SUT, it may be better to define proper equality members in the object’s class. You can then compare the object to an expected value using a single assertion.

尽管如此，你需要注意断言部分增长过大：这可能是生产代码中缺少抽象的标志。例如，与其断言由 SUT 返回的对象内的所有属性，不如在对象的类中定义适当的相等成员。然后，你可以使用一个单一的断言将该对象与预期值进行比较。

### [](#3-1-6-复原阶段 "3.1.6 复原阶段")3.1.6 复原阶段

**What about the teardown phase?**

Some people also distinguish a fourth section, teardown, which comes after arrange, act, and assert. For example, you can use this section to remove any files created by the test, close a database connection, and so on. The teardown is usually represented by a separate method, which is reused across all tests in the class. Thus, I don’t include this phase in the AAA pattern.

有些人还区分了第四部分，即复原，它在准备、执行和断言之后。例如，你可以使用这一部分来删除测试所创建的任何文件，关闭数据库连接，等等。复原通常由一个单独的方法表示，在类的所有测试中重复使用。因此，我在 AAA 模式中不包括这个阶段。

Note that most unit tests don’t need teardown. Unit tests don’t talk to out-of-process dependencies and thus don’t leave side effects that need to be disposed of. That’s a realm of integration testing. We’ll talk more about how to properly clean up after integration tests in part 3.

请注意，大多数单元测试都不需要复原。单元测试不与进程外的依赖通信，因此不会留下需要处理的副作用。这是集成测试的一个领域。我们将在第三部分讨论如何正确清理集成测试后的问题。

### [](#3-1-7-区分被测系统 "3.1.7 区分被测系统")3.1.7 区分被测系统

**Differentiating the system under test**

The SUT plays a significant role in tests. It provides an entry point for the behavior you want to invoke in the application. As we discussed in the previous chapter, this behavior can span across as many as several classes or as little as a single method. But there can be only one entry point: one class that triggers that behavior.

SUT 在测试中起着重要作用。它为你想在应用程序中调用的行为提供了一个入口点。正如我们在前一章所讨论的，这个行为可以跨越多个类，也可以是一个单一的方法。但只能有一个入口点：一个触发该行为的类。

Thus it’s important to differentiate the SUT from its dependencies, especially when there are quite a few of them, so that you don’t need to spend too much time figuring out who is who in the test. To do that, always name the SUT in tests sut. The following listing shows how CalculatorTests would look after renaming the Calculator instance

因此，将 SUT 与它的依赖区分开来是很重要的，特别是在有很多依赖的时候，这样你就不需要花太多的时间去弄清楚测试中谁是谁。为了做到这一点，总是在测试中将 SUT 命名为 sut。下面的清单显示了重命名 Calculator 实例后 CalculatorTests 的样子

Listing 3.4 Differentiating the SUT from its dependencies

![image-20230409204032581](~/assets/images/unit-testing-3/image-20230409204032581.png)

### [](#3-1-8-删除测试中的准备、执行和断言的注释 "3.1.8 删除测试中的准备、执行和断言的注释")3.1.8 删除测试中的准备、执行和断言的注释

**Dropping the arrange, act, and assert comments from tests**

Just as it’s important to set the SUT apart from its dependencies, it’s also important to differentiate the three sections from each other, so that you don’t spend too much time figuring out what section a particular line in the test belongs to. One way to do that is to put // Arrange, // Act, and // Assert comments before the beginning of each section. Another way is to separate the sections with empty lines, as shown next.

正如将 SUT 与它的依赖关系区分开来一样，将这三个部分相互区分开来也很重要，这样你就不会花太多时间去弄清楚测试中的某一行属于哪个部分。一种方法是在每个部分的开始前加上 //准备、//执行 和 //断言的注释。另一种方法是用空行来分隔各部分，如下面所示。

Listing 3.5 Calculator with sections separated by empty lines 用空行分隔各部分的 Calculator

![image-20230409204100952](~/assets/images/unit-testing-3/image-20230409204100952.png)

Separating sections with empty lines works great in most unit tests. It allows you to keep a balance between brevity and readability. It doesn’t work as well in large tests, though, where you may want to put additional empty lines inside the arrange section to differentiate between configuration stages. This is often the case in integration tests—they frequently contain complicated setup logic. Therefore,

在大多数单元测试中，用空行来分隔各部分非常有效。它允许你在简洁性和可读性之间保持平衡。但在大型测试中，它的效果并不理想，你可能想在准备部分中增加空行来区分配置阶段。在集成测试中经常出现这种情况–它们经常包含复杂的设置逻辑。因此

*   Drop the section comments in tests that follow the AAA pattern and where you can avoid additional empty lines inside the arrange and assert sections. 在遵循 AAA 模式的测试中弃用阶段注释，这样可以避免在准备和断言部分增加空行。
*   Keep the section comments otherwise. 否则保留阶段注释。

## [](#3-2-探索-xUnit-测试框架 "3.2 探索 xUnit 测试框架")3.2 探索 xUnit 测试框架

**Exploring the xUnit testing framework**

In this section, I give a brief overview of unit testing tools available in .NET, and their features. I’m using xUnit ([https://github.com/xunit/xunit](https://github.com/xunit/xunit)) as the unit testing framework (note that you need to install the xunit.runner.visualstudio NuGet package in order to run xUnit tests from Visual Studio). Although this framework works in .NET only, every object-oriented language (Java, C++, JavaScript, and so on) has unit testing frameworks, and all those frameworks look quite similar to each other. If you’ve worked with one of them, you won’t have any issues working with another.

在这一节中，我简要介绍了 .NET 中可用的单元测试工具，以及它们的特点。我使用 xUnit（[https://github.com/xunit/xunit）作为单元测试框架（注意，你需要安装xunit.runner.visualstudio](https://github.com/xunit/xunit%EF%BC%89%E4%BD%9C%E4%B8%BA%E5%8D%95%E5%85%83%E6%B5%8B%E8%AF%95%E6%A1%86%E6%9E%B6%EF%BC%88%E6%B3%A8%E6%84%8F%EF%BC%8C%E4%BD%A0%E9%9C%80%E8%A6%81%E5%AE%89%E8%A3%85xunit.runner.visualstudio) NuGet包，以便从Visual Studio运行xUnit测试）。虽然这个框架只适用于 .NET，但每一种面向对象的语言（Java、C++、JavaScript等）都有单元测试框架，而且所有这些框架看起来都很相似。如果你使用过其中一个框架，那么你使用另一个框架就不会有任何问题。

In .NET alone, there are several alternatives to choose from, such as NUnit ([https://github.com/nunit/nunit](https://github.com/nunit/nunit)) and the built-in Microsoft MSTest. I personally prefer xUnit for the reasons I’ll describe shortly, but you can also use NUnit; these two frameworks are pretty much on par in terms of functionality. I don’t recommend MSTest, though; it doesn’t provide the same level of flexibility as xUnit and NUnit. And don’t take my word for it—even people inside Microsoft refrain from using MSTest. For example, the ASP.NET Core team uses xUnit.

仅在 .NET 中，就有几个备选方案可供选择，如 NUnit（[https://github.com/nunit/nunit）和内置的微软](https://github.com/nunit/nunit%EF%BC%89%E5%92%8C%E5%86%85%E7%BD%AE%E7%9A%84%E5%BE%AE%E8%BD%AF) MSTest。我个人更喜欢 xUnit，原因我很快就会介绍，但你也可以使用 NUnit；这两个框架在功能上基本是一致的。但我不推荐 MSTest；它不能提供与 xUnit 和NUnit 相同的灵活性。不相信我的话，即使是微软内部的人也不愿意使用 MSTest。例如，ASP.NET Core 团队使用 xUnit。

I prefer xUnit because it’s a cleaner, more concise version of NUnit. For example, you may have noticed that in the tests I’ve brought up so far, there are no frameworkrelated attributes other than \[Fact\], which marks the method as a unit test so the unit testing framework knows to run it. There are no \[TestFixture\] attributes; any public class can contain a unit test. There’s also no \[SetUp\] or \[TearDown\]. If you need to share configuration logic between tests, you can put it inside the constructor. And if you need to clean something up, you can implement the IDisposable interface, as shown in this listing.

我更喜欢 xUnit，因为它是 NUnit 的一个更干净、更简洁的版本。例如，你可能已经注意到，在我目前提出的测试中，除了 \[Fact\]，没有任何与框架相关的属性，\[Fact\] 将方法标记为单元测试，这样单元测试框架就知道要运行它。没有 \[TestFixture\] 属性；任何公共类都可以包含一个单元测试。也没有 \[SetUp\] 或 \[TearDown\]。如果你需要在测试之间共享配置逻辑，你可以把它放在构造函数中。而如果你需要清理一些东西，你可以实现 IDisposable 接口，如该清单所示。

Listing 3.6 Arrangement and teardown logic, shared by all tests 准备和复原逻辑，由所有测试共享

![image-20230409204327740](~/assets/images/unit-testing-3/image-20230409204327740.png)

As you can see, the xUnit authors took significant steps toward simplifying the framework. A lot of notions that previously required additional configuration (like \[TestFixture\] or \[SetUp\] attributes) now rely on conventions or built-in language constructs.

正如你所看到的，xUnit 作者在简化框架方面采取了重大步骤。很多以前需要额外配置的概念（如 \[TestFixture\] 或 \[SetUp\] 属性）现在都依赖于惯例或内置语言结构。

I particularly like the \[Fact\] attribute, specifically because it’s called Fact and not Test. It emphasizes the rule of thumb I mentioned in the previous chapter: each test should tell a story. This story is an individual, atomic scenario or fact about the problem domain, and the passing test is a proof that this scenario or fact holds true. If the test fails, it means either the story is no longer valid and you need to rewrite it, or the system itself has to be fixed

我特别喜欢 \[Fact\] 属性，特别是因为它被称为 Fact 而不是 Test。它强调了我在上一章提到的经验法则：每个测试应该讲述一个故事。这个故事是关于问题领域的一个单独的、原子性的场景或事实，而通过的测试是这个场景或事实成立的一个证明。如果测试失败，这意味着要么故事不再有效，你需要重写它，要么系统本身必须被修复。

I encourage you to adopt this way of thinking when you write unit tests. Your tests shouldn’t be a dull enumeration of what the production code does. Rather, they should provide a higher-level description of the application’s behavior. Ideally, this description should be meaningful not just to programmers but also to business people.

我鼓励你在写单元测试时采用这种思维方式。你的测试不应该是对生产代码的枯燥列举。相反，他们应该对应用程序的行为提供一个更高层次的描述。理想情况下，这种描述不仅对程序员有意义，对业务人员也有意义。

## [](#3-3-在测试之间重复使用测试夹具 "3.3 在测试之间重复使用测试夹具")3.3 在测试之间重复使用测试夹具

**Reusing test fixtures between tests**

It’s important to know how and when to reuse code between tests. Reusing code between arrange sections is a good way to shorten and simplify your tests, and this section shows how to do that properly

知道如何以及何时在测试之间重用代码是很重要的。在准备部分之间重用代码是缩短和简化测试的一个好方法，本节展示了如何正确地做到这一点

I mentioned earlier that often, fixture arrangements take up too much space. It makes sense to extract these arrangements into separate methods or classes that you then reuse between tests. There are two ways you can perform such reuse, but only one of them is beneficial; the other leads to increased maintenance costs.

我在前面提到，通常情况下，夹具准备占用了太多的空间。将这些准备提取到单独的方法或类中是有意义的，然后在测试之间重复使用。有两种方法可以进行这种重用，但只有一种是有益的；另一种会导致维护成本的增加。

> Test fixture 测试夹具
> 
> The term test fixture has two common meanings: 测试夹具这个术语有两个常见的含义：
> 
> 1.  A test fixture is an object the test runs against. This object can be a regular dependency—an argument that is passed to the SUT. It can also be data in the database or a file on the hard disk. Such an object needs to remain in a known, fixed state before each test run, so it produces the same result. Hence the word fixture. 测试夹具是一个测试运行的对象。这个对象可以是一个常规的依赖–一个传递给 SUT 的参数。它也可以是数据库中的数据或硬盘上的一个文件。这样的对象需要在每次测试运行前保持一个已知的、固定的状态，所以它产生相同的结果。因此就有了 fixture 这个词。
> 2.  The other definition comes from the NUnit testing framework. In NUnit, TestFixture is an attribute that marks a class containing tests. 另一个定义来自于 NUnit 测试框架。在 NUnit 中，TestFixture 是一个属性，它标志着一个包含测试的类。
> 
> I use the first definition throughout this book 我在本书中使用第一个定义

The first—incorrect—way to reuse test fixtures is to initialize them in the test’s constructor (or the method marked with a \[SetUp\] attribute if you are using NUnit), as shown next.

重用测试夹具的第一种正确方法是在测试的构造函数中初始化它们（如果你使用 NUnit，则是用 \[SetUp\] 属性标记的方法），如下所示。

Listing 3.7 Extracting the initialization code into the test constructor 将初始化代码提取到测试构造函数中

![image-20230409204513596](~/assets/images/unit-testing-3/image-20230409204513596.png)

The two tests in listing 3.7 have common configuration logic. In fact, their arrange sections are the same and thus can be fully extracted into CustomerTests’s constructor— which is precisely what I did here. The tests themselves no longer contain arrangements.

列表 3.7 中的两个测试有共同的配置逻辑。事实上，它们的准备部分是相同的，因此可以完全提取到 CustomerTests 的构造函数中–这正是我在这里所做的。测试本身不再包含准备。

With this approach, you can significantly reduce the amount of test code—you can get rid of most or even all test fixture configurations in tests. But this technique has two significant drawbacks:

通过这种方法，你可以大大减少测试代码的数量–你可以在测试中摆脱大部分甚至所有的测试夹具配置。但这种技术有两个明显的缺点：

*   It introduces high coupling between tests. 它引入了测试之间的高耦合性。
*   It diminishes test readability. 它降低了测试的可读性。

Let’s discuss these drawbacks in more detail. 让我们更详细地讨论这些缺点。

### [](#3-3-1-测试之间的高耦合是一种反模式 "3.3.1 测试之间的高耦合是一种反模式")3.3.1 测试之间的高耦合是一种反模式

**High coupling between tests is an anti-pattern**

In the new version, shown in listing 3.7, all tests are coupled to each other: a modification of one test’s arrangement logic will affect all tests in the class. For example, changing this line

在新的版本中，如列表 3.7 所示，所有的测试都是相互耦合的：对一个测试的准备逻辑的修改将影响该类中的所有测试。例如，改变这一行

```csharp
1   _store.AddInventory(Product.Shampoo, 10);
```

to this

```csharp
1   _store.AddInventory(Product.Shampoo, 15);
```

would invalidate the assumption the tests make about the store’s initial state and therefore would lead to unnecessary test failures.

会使测试对商店初始状态的假设失效，因此会导致不必要的测试失败。

That’s a violation of an important guideline: a modification of one test should not affect other tests. This guideline is similar to what we discussed in chapter 2—that tests should run in isolation from each other. It’s not the same, though. Here, we are talking about independent modification of tests, not independent execution. Both are important attributes of a well-designed test.

这就违反了一个重要的准则：对一个测试的修改不应影响其他测试。这条准则类似于我们在第 2 章中所讨论的，即测试应该在相互隔离的情况下运行。不过，这并不一样。这里，我们谈论的是测试的独立修改，而不是独立执行。两者都是精心设计的测试的重要属性。

To follow this guideline, you need to avoid introducing shared state in test classes. These two private fields are examples of such a shared state:

为了遵循这一准则，你需要避免在测试类中引入共享状态。这两个私有字段就是这种共享状态的例子：

```csharp
1   private readonly Store _store;
2   private readonly Customer _sut;
```

### [](#3-3-2-在测试中使用构造函数会降低测试的可读性 "3.3.2 在测试中使用构造函数会降低测试的可读性")3.3.2 在测试中使用构造函数会降低测试的可读性

**The use of constructors in tests diminishes test readability**

The other drawback to extracting the arrangement code into the constructor is diminished test readability. You no longer see the full picture just by looking at the test itself. You have to examine different places in the class to understand what the test method does.

将准备代码提取到构造函数中的另一个缺点是削弱了测试的可读性。你不再能仅仅通过查看测试本身看到全貌。你必须检查类中的不同地方以了解测试方法的作用。

Even if there’s not much arrangement logic—say, only instantiation of the fixtures— you are still better off moving it directly to the test method. Otherwise, you’ll wonder if it’s really just instantiation or something else being configured there, too. A self-contained test doesn’t leave you with such uncertainties.

即使没有太多的准备逻辑–比如说，只有测试夹具的实例化–你仍然最好把它直接移到测试方法中。否则，你会怀疑是否真的只是实例化或其他东西也被配置在那里。一个独立的测试不会给你留下这样的不确定因素。

### [](#3-3-3-重复使用测试夹具的更好方法 "3.3.3 重复使用测试夹具的更好方法")3.3.3 重复使用测试夹具的更好方法

**A better way to reuse test fixtures**

The use of the constructor is not the best approach when it comes to reusing test fixtures. The second way—the beneficial one—is to introduce private factory methods in the test class, as shown in the following listing.

当涉及到重复使用测试夹具时，使用构造函数不是最好的方法。第二种方式–有益的方式是在测试类中引入私有工厂方法，如下面清单所示。

Listing 3.8 Extracting the common initialization code into private factory methods 将普通初始化代码提取到私有工厂方法中

```csharp
1   public class CustomerTests
2   {
3   	[Fact]
4   	public void Purchase_succeeds_when_enough_inventory()
5   	{
6       	Store store = CreateStoreWithInventory(Product.Shampoo, 10);
7   		Customer sut = CreateCustomer();
8   		bool success = sut.Purchase(store, Product.Shampoo, 5);
9   		Assert.True(success);
10  		Assert.Equal(5, store.GetInventory(Product.Shampoo));
11  	}
12  	[Fact]
13  	public void Purchase_fails_when_not_enough_inventory()
14  	{
15  		Store store = CreateStoreWithInventory(Product.Shampoo, 10);
16  		Customer sut = CreateCustomer();
17  		bool success = sut.Purchase(store, Product.Shampoo, 15);
18  		Assert.False(success);
19  		Assert.Equal(10, store.GetInventory(Product.Shampoo));
20  	}
21  	private Store CreateStoreWithInventory(
22  	Product product, int quantity)
23  	{
24  		Store store = new Store();
25  		store.AddInventory(product, quantity);
26  		return store;
27  	}
28  	private static Customer CreateCustomer()
29  	{
30  		return new Customer();
31  	}
32  }
```

By extracting the common initialization code into private factory methods, you can also shorten the test code, but at the same time keep the full context of what’s going on in the tests. Moreover, the private methods don’t couple tests to each other as long as you make them generic enough. That is, allow the tests to specify how they want the fixtures to be created.

通过将通用的初始化代码提取到私有工厂方法中，你也可以缩短测试代码，但同时保持测试中发生的全部内容。此外，只要你让它们有足够的通用性，私有方法就不会使测试相互耦合。也就是说，允许测试指定他们希望如何创建夹具。

Look at this line, for example:

例如,看看这一行:

```csharp
1   Store store = CreateStoreWithInventory(Product.Shampoo, 10);
```

The test explicitly states that it wants the factory method to add 10 units of shampoo to the store. This is both highly readable and reusable. It’s readable because you don’t need to examine the internals of the factory method to understand the attributes of the created store. It’s reusable because you can use this method in other tests, too.

该测试明确指出，它希望工厂方法向商店添加 10 个单位的洗发水。这既是高度可读的，也是可重用的。它是可读的，因为你不需要检查工厂方法的内部结构来了解创建的商店的属性。它是可重复使用的，因为你也可以在其他测试中使用这个方法。

Note that in this particular example, there’s no need to introduce factory methods, as the arrangement logic is quite simple. View it merely as a demonstration

请注意，在这个特殊的例子中，没有必要引入工厂方法，因为准备逻辑是非常简单的。仅仅把它看作是一个示范

There’s one exception to this rule of reusing test fixtures. You can instantiate a fixture in the constructor if it’s used by all or almost all tests. This is often the case for integration tests that work with a database. All such tests require a database connection, which you can initialize once and then reuse everywhere. But even then, it would make more sense to introduce a base class and initialize the database connection in that class’s constructor, not in individual test classes. See the following listing for an example of common initialization code in a base class.

重用测试夹具的这个规则有一个例外。如果一个夹具被所有或几乎所有的测试使用，你可以在构造函数中把它实例化。这通常是与数据库一起工作的集成测试的情况。所有这些测试都需要一个数据库连接，你可以初始化一次，然后到处重用。但即使如此，引入一个基类并在该类的构造函数中初始化数据库连接，而不是在各个测试类中，会更有意义。请看下面的清单，这是一个基类中常用初始化代码的例子。

Listing 3.9 Common initialization code in a base class 基类中常见的初始化代码

```csharp
1   public class CustomerTests : IntegrationTests
2   {
3   	[Fact]
4   	public void Purchase_succeeds_when_enough_inventory()
5   	{
6   		/* use _database here */
7   	}
8   }
9   
10  public abstract class IntegrationTests : IDisposable
11  {
12  		protected readonly Database _database;
13  		protected IntegrationTests()
14  		{
15  			_database = new Database();
16  		}
17          
18  		public void Dispose()
19  		{
20  			_database.Dispose();
21  		}
22  }
```

Notice how CustomerTests remains constructor-less. It gets access to the \_database instance by inheriting from the IntegrationTests base class.

注意 CustomerTests 是如何保持无构造函数的。它通过继承 IntegrationTests 基类获得对 \_database 实例的访问。

## [](#3-4-命名一个单元测试 "3.4 命名一个单元测试")3.4 命名一个单元测试

**Naming a unit test**

It’s important to give expressive names to your tests. Proper naming helps you understand what the test verifies and how the underlying system behaves.

给你的测试起一个有表现力的名字是很重要的。正确的命名可以帮助你理解测试所验证的内容和底层系统的行为方式。

So, how should you name a unit test? I’ve seen and tried a lot of naming conventions over the past decade. One of the most prominent, and probably least helpful, is the following convention:

那么，你应该如何命名一个单元测试？在过去的十年中，我看到并尝试了很多命名规则。其中最突出的，也可能是**最没有帮助**的，是下面这个约定：

```csharp
1   [MethodUnderTest]_[Scenario]_[ExpectedResult]
```

where

*   MethodUnderTest is the name of the method you are testing. MethodUnderTest是你要测试的方法的名称。
*   Scenario is the condition under which you test the method. Scenario是你测试该方法的条件。
*   ExpectedResult is what you expect the method under test to do in the current scenario. ExpectedResult是你希望被测试的方法在当前场景下做什么。

It’s unhelpful specifically because it encourages you to focus on implementation details instead of the behavior.

这是很无用的，因为它鼓励你专注于实现细节而不是行为。

Simple phrases in plain English do a much better job: they are more expressive and don’t box you in a rigid naming structure. With simple phrases, you can describe the system behavior in a way that’s meaningful to a customer or a domain expert. To give you an example of a test titled in plain English, here’s the test from listing 3.5 once again:

简单的英语短语可以做得更好：它们更有表现力，不会把你框在一个僵硬的命名结构中。通过简单的短语，你可以用一种对客户或领域专家有意义的方式来描述系统的行为。为了给你一个用简单的英语命名的测试的例子，这里是列表 3.5 中的测试，再一次：

```csharp
1   public class CalculatorTests
2   {
3   	[Fact]
4   	public void Sum_of_two_numbers()
5   	{
6   		double first = 10;
7   		double second = 20;
8   		var sut = new Calculator();
9   		double result = sut.Sum(first, second);
10  		Assert.Equal(30, result);
11  	}
12  }
```

How could the test’s name (Sum\_of\_two\_numbers) be rewritten using the \[MethodUnderTest\]_\[Scenario\]_\[ExpectedResult\] convention? Probably something like this:

如何使用\[MethodUnderTest\]_\[Scenario\]_\[ExpectedResult\]惯例改写测试的名称（Sum\_of\_two\_numbers）？可能是这样的：

```csharp
1   public void Sum_TwoNumbers_ReturnsSum()
```

The method under test is Sum, the scenario includes two numbers, and the expected result is a sum of those two numbers. The new name looks logical to a programmer’s eye, but does it really help with test readability? Not at all. It’s Greek to an uninformed person. Think about it: Why does Sum appear twice in the name of the test? And what is this Returns phrasing all about? Where is the sum returned to? You can’t know.

被测试的方法是 Sum，场景包括两个数字，预期结果是这两个数字的和。在程序员的眼里，这个新名字看起来很合理，但它真的有助于测试的可读性吗？一点也没有。对于一个不知情的人来说，这就是希腊语。想一想吧： 为什么 Sum 在测试的名称中出现两次？这个返回的措辞又是怎么回事？总数被返回到哪里？你不可能知道。

Some might argue that it doesn’t really matter what a non-programmer would think of this name. After all, unit tests are written by programmers for programmers, not domain experts. And programmers are good at deciphering cryptic names—it’s their job!

有些人可能会说，非程序员对这个名字的看法其实并不重要。毕竟，单元测试是由程序员为程序员写的，而不是领域专家。而程序员擅长破译神秘的名字–这是他们的工作!

This is true, but only to a degree. Cryptic names impose a cognitive tax on everyone, programmers or not. They require additional brain capacity to figure out what exactly the test verifies and how it relates to business requirements. This may not seem like much, but the mental burden adds up over time. It slowly but surely increases the maintenance cost for the entire test suite. It’s especially noticeable if you return to the test after you’ve forgotten about the feature’s specifics, or try to understand a test written by a colleague. Reading someone else’s code is already difficult enough—any help understanding it is of considerable use.

这是真的，但只是在一定程度上。隐秘的名字对每个人都是一种认知上的负担，不管是不是程序员。他们需要额外的脑容量来弄清楚测试到底验证了什么，以及它与业务需求的关系。这可能看起来不多，但随着时间的推移，心理负担会增加。它缓慢但肯定地增加了整个测试套件的维护成本。如果你在忘记了功能的具体细节后再回到测试中，或者试图理解同事写的测试，这一点尤其明显。阅读别人的代码已经很困难了–任何帮助理解代码都是相当有用的。

Here are the two versions again: 下面是这两个版本：

```csharp
1   public void Sum_of_two_numbers()
2   public void Sum_TwoNumbers_ReturnsSum()
```

The initial name written in plain English is much simpler to read. It is a down-to-earth description of the behavior under test.

用普通英语写的初始名称读起来要简单得多。它是对被测试行为的朴实描述。

### [](#3-4-1-单元测试命名指南 "3.4.1 单元测试命名指南")3.4.1 单元测试命名指南

**Unit test naming guidelines**

Adhere to the following guidelines to write expressive, easily readable test names:

遵守以下准则，写出富有表现力、易读的测试名称：

*   Don’t follow a rigid naming policy. You simply can’t fit a high-level description of a complex behavior into the narrow box of such a policy. Allow freedom of expression. 不要遵循僵化的命名政策。你根本无法将复杂行为的高级描述纳入这种政策的狭小范围内。允许自由表达。
*   Name the test as if you were describing the scenario to a non-programmer who is familiar with the problem domain. A domain expert or a business analyst is a good example. 命名测试，就像你向一个熟悉问题领域的非程序员描述这个场景一样。领域专家或业务分析员是一个很好的例子。
*   Separate words with underscores. Doing so helps improve readability, especially in long names. 用下划线将单词分开。这样做有助于提高可读性，特别是在长名称中。

Notice that I didn’t use underscores when naming the test class, CalculatorTests. Normally, the names of classes are not as long, so they read fine without underscores. 注意，我在命名测试类 CalculatorTests 时没有使用下划线。通常情况下，类的名字没有那么长，所以不用下划线也能读懂。

Also notice that although I use the pattern \[ClassName\]Tests when naming test classes, it doesn’t mean the tests are limited to verifying only that class. Remember, the unit in unit testing is a unit of behavior, not a class. This unit can span across one or several classes; the actual size is irrelevant. Still, you have to start somewhere. View the class in \[ClassName\]Tests as just that: an entry point, an API, using which you can verify a unit of behavior.

同样注意到，尽管我在命名测试类时使用了 \[ClassName\]Tests 这一模式，但这并不意味着测试只限于验证该类。**记住，单元测试中的单元是一个行为单元，而不是一个类。**这个单元可以跨越一个或几个类；实际大小无关紧要。不过，你还是得从某个地方开始。把\[ClassName\] 测试中的类看作是：一个入口，一个API，你可以用它来验证一个行为单元。

> 译者注：如果将测试文档化，那么测试就是对 API 能力的描述。

### [](#3-4-2-示例：根据准则重命名测试 "3.4.2 示例：根据准则重命名测试")3.4.2 示例：根据准则重命名测试

**Example: Renaming a test toward the guidelines**

Let’s take a test as an example and try to gradually improve its name using the guidelines I just outlined. In the following listing, you can see a test verifying that a delivery with a past date is invalid. The test’s name is written using the rigid naming policy that doesn’t help with the test readability.

让我们以一个测试为例，尝试用我刚才概述的准则逐步改进其名称。在下面的列表中，你可以看到一个测试，验证一个日期已过的交货是无效的。这个测试的名字是用僵硬的命名策略写的，对测试的可读性没有帮助。

Listing 3.10 A test named using the rigid naming policy 一个使用严格的命名策略命名的测试

```csharp
1   [Fact]
2   public void IsDeliveryValid_InvalidDate_ReturnsFalse()
3   {
4   	DeliveryService sut = new DeliveryService();
5   	DateTime pastDate = DateTime.Now.AddDays(-1);
6   	Delivery delivery = new Delivery
7   	{
8   		Date = pastDate
9   	};
10      bool isValid = sut.IsDeliveryValid(delivery);
11  	Assert.False(isValid);
12  }
```

This test checks that DeliveryService properly identifies a delivery with an incorrect date as invalid. How would you rewrite the test’s name in plain English? The following would be a good first try:

这个测试检查 DeliveryService 是否正确地将日期不正确的交付物识别为无效。你如何用简单的英语改写这个测试的名字？以下是一个很好的初步尝试：

```csharp
1   public void Delivery_with_invalid_date_should_be_considered_invalid()
```

Notice two things in the new version: 注意新版本中的两件事：

*   The name now makes sense to a non-programmer, which means programmers will have an easier time understanding it, too. 现在的名字对非程序员来说是有意义的，这意味着程序员也会更容易理解它。
*   The name of the SUT’s method—IsDeliveryValid—is no longer part of the test’s name. SUT 的方法名称 -IsDeliveryValid- 不再是测试名称的一部分。

The second point is a natural consequence of rewriting the test’s name in plain English and thus can be easily overlooked. However, this consequence is important and can be elevated into a guideline of its own.

第二点是用普通英语改写测试名称的自然结果，因此很容易被忽视。然而，这个结果是很重要的，可以上升为一个自己的准则。

> Method under test in the test’s name 测试名称中的被测方法
> 
> Don’t include the name of the SUT’s method in the test’s name. 不要在测试名称中包括 SUT 的方法的名称。
> 
> Remember, you don’t test code, you test application behavior. Therefore, it doesn’t matter what the name of the method under test is. As I mentioned previously, the SUT is just an entry point: a means to invoke a behavior. You can decide to rename the method under test to, say, IsDeliveryCorrect, and it will have no effect on the SUT’s behavior. On the other hand, if you follow the original naming convention, you’ll have to rename the test. This once again shows that targeting code instead of behavior couples tests to that code’s implementation details, which negatively affects the test suite’s maintainability. More on this issue in chapter 5.
> 
> **记住，你不是在测试代码，而是在测试应用行为。**因此，被测方法的名称是什么并不重要。正如我之前提到的，SUT 只是一个入口点：一个调用行为的手段。你可以决定将被测方法改名为 IsDeliveryCorrect，这对 SUT 的行为没有影响。另一方面，如果你遵循原来的命名规则，你将不得不重新命名测试。这再次表明，以代码而不是行为为目标，将测试与代码的实现细节联系起来，这对测试套件的可维护性产生了负面影响。更多关于这个问题的内容在第五章。
> 
> The only exception to this guideline is when you work on utility code. Such code doesn’t contain business logic—its behavior doesn’t go much beyond simple auxiliary functionality and thus doesn’t mean anything to business people. It’s fine to use the SUT’s method names there.
> 
> 这条准则的唯一例外是当你工作在工具代码上时。这样的代码不包含业务逻辑–它的行为并没有超出简单的辅助功能，因此对业务人员来说没有任何意义。在这里使用 SUT 的方法名是可以的。

But let’s get back to the example. The new version of the test’s name is a good start, but it can be improved further. What does it mean for a delivery date to be invalid, exactly? From the test in listing 3.10, we can see that an invalid date is any date in the past. This makes sense—you should only be allowed to choose a delivery date in the future.

但让我们回到这个例子上。新版测试的名称是一个好的开始，但还可以进一步改进。交付日期无效到底是什么意思？从列表 3.10 的测试中，我们可以看到无效的日期是过去的任何日期。你应该只被允许选择一个未来的交货日期是有道理的。

So let’s be specific and reflect this knowledge in the test’s name:

所以让我们具体一点，在测试的名称中反映这个知识：

```csharp
1   public void Delivery_with_past_date_should_be_considered_invalid()
```

This is better but still not ideal. It’s too verbose. We can get rid of the word considered without any loss of meaning:

这样做比较好，但仍然不理想。它太啰嗦了。我们可以去掉 considered 这个词而不损失任何意义：

```csharp
1   public void Delivery_with_past_date_should_be_invalid()
```

The wording should be is another common anti-pattern. Earlier in this chapter, I mentioned that a test is a single, atomic fact about a unit of behavior. There’s no place for a wish or a desire when stating a fact. Name the test accordingly—replace should be with is:

**should be 的措辞是另一个常见的反模式。在本章的前面，我提到测试是关于一个行为单元的单一的、原子性的事实。在陈述一个事实时，没有地方可以容纳愿望或欲望。**给测试起一个相应的名字–用 is 来代替应该是：

```csharp
1   public void Delivery_with_past_date_is_invalid()
```

And finally, there’s no need to avoid basic English grammar. Articles help the test read flawlessly. Add the article a to the test’s name:

最后，没有必要避免基本的英语语法。冠词可以帮助测试无懈可击地阅读。在测试的名称中添加冠词 a：

```csharp
1   public void Delivery_with_a_past_date_is_invalid()
```

There you go. This final version is a straight-to-the-point statement of a fact, which itself describes one of the aspects of the application behavior under test: in this particular case, the aspect of determining whether a delivery can be done.

就这样吧。这个最终版本是对一个事实的直截了当的陈述，它本身描述了被测试的应用程序行为的一个方面：在此特定情况下，确定是否可以完成交付。

## [](#3-5-重构为参数化测试 "3.5 重构为参数化测试")3.5 重构为参数化测试

**Refactoring to parameterized tests**

One test usually is not enough to fully describe a unit of behavior. Such a unit normally consists of multiple components, each of which should be captured with its own test. If the behavior is complex enough, the number of tests describing it can grow dramatically and may become unmanageable. Luckily, most unit testing frameworks provide functionality that allows you to group similar tests using parameterized tests (see figure 3.2).

一个测试通常不足以完全描述一个单元的行为。这样一个单元通常由多个组件组成，每个组件都应该有自己的测试。如果行为足够复杂，描述它的测试数量会急剧增加，可能会变得无法管理。幸运的是，大多数单元测试框架提供的功能，允许你使用参数化测试来分组类似的测试（见图3.2）。

![image-20230409205806727](~/assets/images/unit-testing-3/image-20230409205806727.png)

Figure 3.2 A typical application exhibits multiple behaviors. The greater the complexity of the behavior, the more facts are required to fully describe it. Each fact is represented by a test. Similar facts can be grouped into a single test method using parameterized tests.

图 3.2 一个典型的应用程序表现出多种行为。行为的复杂性越高，需要更多的事实来完全描述它。每个事实都由一个测试来表示。类似的事实可以使用参数化测试分组到一个单一的测试方法中。

In this section, I’ll first show each such behavior component described by a separate test and then demonstrate how these tests can be grouped together.

在本节中，我将首先展示每个这样的行为组件由一个单独的测试来描述，然后演示如何将这些测试组合在一起。

Let’s say that our delivery functionality works in such a way that the soonest allowed delivery date is two days from now. Clearly, the one test we have isn’t enough. In addition to the test that checks for a past delivery date, we’ll also need tests that check for today’s date, tomorrow’s date, and the date after that.

比方说，我们的交付功能的工作方式是，允许的最快交付日期是两天后。显然，我们的一个测试是不够的。除了检查过去交货日期的测试外，我们还需要检查今天的日期、明天的日期和之后的日期的测试。

The existing test is called Delivery\_with\_a\_past\_date\_is\_invalid. We could add three more:

现有的测试叫做 Delivery\_with\_a\_past\_date\_is\_invalid。我们可以再增加三个：

```csharp
1   public void Delivery_for_today_is_invalid()
2   public void Delivery_for_tomorrow_is_invalid()
3   public void The_soonest_delivery_date_is_two_days_from_now()
```

But that would result in four test methods, with the only difference between them being the delivery date.

但这将导致四个测试方法，它们之间唯一的区别是交付日期。

A better approach is to group these tests into one in order to reduce the amount of test code. xUnit (like most other test frameworks) has a feature called parameterized tests that allows you to do exactly that. The next listing shows how such grouping looks. Each InlineData attribute represents a separate fact about the system; it’s a test case in its own right.

一个更好的方法是把这些测试组合成一个，以减少测试代码的数量。xUnit（像大多数其他测试框架）有一个称为参数化测试的功能，允许你这样做。下一个列表显示了这种分组的样子。每个 InlineData 属性代表系统的一个单独的事实；它本身就是一个测试用例。

Listing 3.11 A test that encompasses several facts 一个包含了几个事实的测试

![image-20230409205908954](~/assets/images/unit-testing-3/image-20230409205908954.png)

> TIP
> 
> Notice the use of the \[Theory\] attribute instead of \[Fact\]. A theory is a bunch of facts about the behavior.
> 
> 注意使用 \[Theory\] 属性而不是 \[Fact\]。一个 Theory 是关于行为的一堆 Fact。

Each fact is now represented by an \[InlineData\] line rather than a separate test. I also renamed the test method something more generic: it no longer mentions what constitutes a valid or invalid date.

每个 Fact 现在由\[InlineData\]行表示，而不是一个单独的测试。我还将测试方法重命名为更通用的东西：它不再提及什么是有效或无效的日期。

Using parameterized tests, you can significantly reduce the amount of test code, but this benefit comes at a cost. It’s now hard to figure out what facts the test method represents. And the more parameters there are, the harder it becomes. As a compromise, you can extract the positive test case into its own test and benefit from the descriptive naming where it matters the most—in determining what differentiates valid and invalid delivery dates, as shown in the following listing.

使用参数化测试，你可以大大减少测试代码的数量，但这个好处是有代价的。现在很难弄清楚测试方法代表什么事实。而且参数越多，就越难。作为一种妥协，你可以把正面的测试用例提取到它自己的测试中，并在最重要的地方从描述性命名中获益–确定有效和无效的交付日期的区别，如下面列表所示。

Listing 3.12 Two tests verifying the positive and negative scenarios 两个测试验证正反两方面的情况

```csharp
1   public class DeliveryServiceTests
2   {
3   	[InlineData(-1)]
4   	[InlineData(0)]
5   	[InlineData(1)]
6   	[Theory]
7   	public void Detects_an_invalid_delivery_date(int daysFromNow)
8   	{
9   		/* ... */
10  	}
11  	[Fact]
12  	public void The_soonest_delivery_date_is_two_days_from_now()
13  	{
14  		/* ... */
15  	}
16  }
```

This approach also simplifies the negative test cases, since you can remove the expected Boolean parameter from the test method. And, of course, you can transform the positive test method into a parameterized test as well, to test multiple dates.

这种方法也简化了负面的测试案例，因为你可以从测试方法中删除预期的布尔参数。当然，你也可以将正面测试方法转化为参数化测试，以测试多个日期。

As you can see, there’s a trade-off between the amount of test code and the readability of that code. As a rule of thumb, keep both positive and negative test cases together in a single method only when it’s self-evident from the input parameters which case stands for what. Otherwise, extract the positive test cases. And if the behavior is too complicated, don’t use the parameterized tests at all. Represent each negative and positive test case with its own test method.

**正如你所看到的，在测试代码的数量和该代码的可读性之间有一个权衡。作为一个经验法则，只有在输入参数不言自明的情况下，才将正面和负面的测试用例放在一个方法中，哪种情况代表什么。否则，提取正面的测试用例。如果行为太复杂，就不要使用参数化测试。用它自己的测试方法来表示每个消极和积极的测试案例。**

### [](#3-5-1-为参数化测试生成数据 "3.5.1 为参数化测试生成数据")3.5.1 为参数化测试生成数据

**Generating data for parameterized tests**

There are some caveats in using parameterized tests (at least, in .NET) that you need to be aware of. Notice that in listing 3.11, I used the daysFromNow parameter as an input to the test method. Why not the actual date and time, you might ask? Unfortunately, the following code won’t work:

在使用参数化测试时有一些注意事项（至少在 .NET 中），你需要注意的。注意，在列表 3.11 中，我使用参数 daysFromNow 作为测试方法的输入。你可能会问，为什么不是实际的日期和时间？不幸的是，下面的代码将无法工作：

```csharp
1   [InlineData(DateTime.Now.AddDays(-1), false)]
2   [InlineData(DateTime.Now, false)]
3   [InlineData(DateTime.Now.AddDays(1), false)]
4   [InlineData(DateTime.Now.AddDays(2), true)]
5   [Theory]
6   public void Can_detect_an_invalid_delivery_date(
7   	DateTime deliveryDate,
8   	bool expected)
9   {
10  	DeliveryService sut = new DeliveryService();
11  	Delivery delivery = new Delivery
12  	{
13  		Date = deliveryDate
14  	};
15  	bool isValid = sut.IsDeliveryValid(delivery);
16  	Assert.Equal(expected, isValid);
17  }
```

In C#, the content of all attributes is evaluated at compile time. You have to use only those values that the compiler can understand, which are as follows:

在 C# 中，所有属性的内容都是在编译时评估的。你必须只使用编译器能够理解的那些值，这些值如下：

*   Constants
*   Literals
*   typeof() expressions

The call to DateTime.Now relies on the .NET runtime and thus is not allowed.

对 DateTime.Now 的调用依赖于 .NET 运行时，因此是不允许的。

There is a way to overcome this problem. xUnit has another feature that you can use to generate custom data to feed into the test method: \[MemberData\]. The next listing shows how we can rewrite the previous test using this feature.

有一个方法可以克服这个问题。xUnit 有另一个功能，你可以用它来生成自定义的数据，输入到测试方法中： \[MemberData\]。下一个列表显示了我们如何使用这个功能重写之前的测试。

Listing 3.13 Generating complex data for the parameterized test 为参数化测试生成复杂数据

```csharp
1   [Theory]
2   [MemberData(nameof(Data))]
3   public void Can_detect_an_invalid_delivery_date(
4   	DateTime deliveryDate,
5   	bool expected)
6   {
7   	/* ... */
8   }
9   
10  public static List<object[]> Data()
11  {
12  	return new List<object[]>
13  	{
14  	new object[] { DateTime.Now.AddDays(-1), false },
15  	new object[] { DateTime.Now, false },
16  	new object[] { DateTime.Now.AddDays(1), false },
17  	new object[] { DateTime.Now.AddDays(2), true }
18  	};
19  }
```

MemberData accepts the name of a static method that generates a collection of input data (the compiler translates nameof(Data) into a “Data” literal). Each element of the collection is itself a collection that is mapped into the two input parameters: deliveryDate and expected. With this feature, you can overcome the compiler’s restrictions and use parameters of any type in the parameterized tests.

MemberData 接受一个静态方法的名称，该方法生成一个输入数据的集合（编译器将 nameof(Data) 翻译成一个 “Data “字面量）。该集合的每个元素本身就是一个集合，被映射到两个输入参数：deliveryDate 和 expected。有了这个特性，你可以克服编译器的限制，在参数化测试中使用任何类型的参数。

## [](#3-6-使用断言库进一步提高测试可读性 "3.6 使用断言库进一步提高测试可读性")3.6 使用断言库进一步提高测试可读性

**Using an assertion library to further improve test readability**

One more thing you can do to improve test readability is to use an assertion library. I personally prefer Fluent Assertions ([https://fluentassertions.com](https://fluentassertions.com/)), but .NET has several competing libraries in this area.

为了提高测试的可读性，你还可以做的一件事是使用断言库。我个人更喜欢 Fluent Assertions（[https://fluentassertions.com），但](https://fluentassertions.com\),但/) .NET 在这个领域有几个竞争性的库。

The main benefit of using an assertion library is how you can restructure the assertions so that they are more readable. Here’s one of our earlier tests:

使用断言库的主要好处是，你可以重组断言，使其更具有可读性。下面是我们早期的一个测试：

```csharp
1   [Fact]
2   public void Sum_of_two_numbers()
3   {
4   	var sut = new Calculator();
5   	double result = sut.Sum(10, 20);
6   	Assert.Equal(30, result);
7   }
```

Now compare it to the following, which uses a fluent assertion:

现在将它与以下内容进行比较,其中使用了流畅的断言:

```csharp
1   [Fact]
2   public void Sum_of_two_numbers()
3   {
4   	var sut = new Calculator();
5   	double result = sut.Sum(10, 20);
6   	result.Should().Be(30);
7   }
```

The assertion from the second test reads as plain English, which is exactly how you want all your code to read. We as humans prefer to absorb information in the form of stories. All stories adhere to this specific pattern:

第二个测试中的断言读起来像普通的英语，这正是你希望你的所有代码读起来的样子。作为人类，我们更喜欢以故事的形式吸收信息。所有的故事都遵循这个特定的模式：

```csharp
1   [Subject] [action] [object].
2       
3   [主体] [动作] [对象].
```

For example,

​ Bob opened the door.

Here, Bob is a subject, opened is an action, and the door is an object. The same rule applies to code. result.Should().Be(30) reads better than Assert.Equal(30, result) precisely because it follows the story pattern. It’s a simple story in which result is a subject, should be is an action, and 30 is an object.

在这里，鲍勃是一个主体，打开是一个动作，而门是一个对象。同样的规则也适用于代码。result.Should().Be(30) 比 Assert.Equal(30, result) 更好读，正是因为它遵循故事模式。这是一个简单的故事，其中 result 是一个主体，should be 是一个动作，30 是一个对象。

> NOTE
> 
> The paradigm of object-oriented programming (OOP) has become a success partly because of this readability benefit. With OOP, you, too, can structure the code in a way that reads like a story.
> 
> 面向对象编程（OOP）的范式之所以成功，部分原因在于这种可读性的好处。有了 OOP，你也可以用一种像故事一样的方式来组织代码。

The Fluent Assertions library also provides numerous helper methods to assert against numbers, strings, collections, dates and times, and much more. The only drawback is that such a library is an additional dependency you may not want to introduce to your project (although it’s for development only and won’t be shipped to production).

Fluent 断言库还提供了大量的辅助方法来断言数字、字符串、集合、日期和时间，以及更多。唯一的缺点是，这样一个库是一个额外的依赖，你可能不想把它引入你的项目（尽管它只用于开发，不会被运到生产中）。

## [](#3-7-总结 "3.7 总结")3.7 总结

**Summary**

*   All unit tests should follow the AAA pattern: arrange, act, assert. If a test has multiple arrange, act, or assert sections, that’s a sign that the test verifies multiple units of behavior at once. If this test is meant to be a unit test, split it into several tests—one per each action. 所有的单元测试应该遵循 AAA 模式：准备，执行，断言。如果一个测试有多个准备，执行，或断言部分，这表明该测试一次验证了多个行为单元。如果这个测试是一个单元测试，把它分成几个测试，每个执行一个测试。
*   More than one line in the act section is a sign of a problem with the SUT’s API. It requires the client to remember to always perform these actions together, which can potentially lead to inconsistencies. Such inconsistencies are called invariant violations. The act of protecting your code against potential invariant violations is called encapsulation. 在执行部分超过一行是 SUT 的 API 有问题的标志。它要求客户端记住总是一起执行这些动作，这有可能导致不一致。这种不一致被称为违反不变性。保护你的代码免受潜在的违反不变性的行为被称为封装。
*   Distinguish the SUT in tests by naming it sut. Differentiate the three test sections either by putting Arrange, Act, and Assert comments before them or by introducing empty lines between these sections. 通过命名 SUT 来区分测试中的 SUT。区分三个测试部分，要么在它们之前加上 Arrange, Act, 和 Assert 注释，要么在这些部分之间引入空行。
*   Reuse test fixture initialization code by introducing factory methods, not by putting this initialization code to the constructor. Such reuse helps maintain a high degree of decoupling between tests and also provides better readability. 通过引入工厂方法来重用测试夹具的初始化代码，而不是把这个初始化代码放到构造器中。这样的重用有助于保持测试之间的高度解耦，也提供更好的可读性。
*   Don’t use a rigid test naming policy. Name each test as if you were describing the scenario in it to a non-programmer who is familiar with the problem domain. Separate words in the test name by underscores, and don’t include the name of the method under test in the test name. 不要使用僵硬的测试命名策略。为每个测试命名，就像你向一个熟悉问题领域的非程序员描述其中的情景一样。在测试名称中用下划线分隔单词，不要在测试名称中包括被测方法的名称。
*   Parameterized tests help reduce the amount of code needed for similar tests. The drawback is that the test names become less readable as you make them more generic. 参数化测试有助于减少类似测试所需的代码量。缺点是，当你让测试名称变得更加通用时，它的可读性会降低。
*   Assertion libraries help you further improve test readability by restructuring the word order in assertions so that they read like plain English. 断言库帮助你进一步提高测试的可读性，通过重组断言中的词序，使它们读起来像普通英语。