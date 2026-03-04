---
publishDate: 2024-09-09T00:00:00Z
title: '单元测试原则、实践与模式（二）'
excerpt: '本章内容涵盖什么是单元测试，共享、私有和不稳定依赖之间的区别，以及单元测试的两个流派：经典和伦敦。'
category: '测试'
tags:
  - 单元测试
metadata:
  canonical: https://nobug.world/blogs/45253/
---

> 译者声明：本译文仅作为学习的记录，不作为任务商业用途，如有侵权请告知我删除。  
> **本文禁止转载！**  
> 请支持原书正版：[https://www.manning.com/books/unit-testing](https://www.manning.com/books/unit-testing)


# [](#第二章-什么是单元测试 "第二章 什么是单元测试")第二章 什么是单元测试

**Chapter 2 What is a unit test?**

This chapter covers 本章内容涵盖

*   What a unit test is 什么是单元测试
*   The differences between shared, private, and volatile dependencies 共享、私有和不稳定依赖之间的区别
*   The two schools of unit testing: classical and London 单元测试的两个流派：经典和伦敦
*   The differences between unit, integration, and end-to-end tests 单元、集成和端到端测试之间的区别

As mentioned in chapter 1, there are a surprising number of nuances in the definition of a unit test. Those nuances are more important than you might think—so much so that the differences in interpreting them have led to two distinct views on how to approach unit testing.

正如第一章所提到的，在单元测试的定义中，有许多令人惊讶的细微差别。这些细微差别比你想象的要重要得多–以至于对它们的解释的差异导致了对如何进行单元测试的两种不同观点。

These views are known as the classical and the London schools of unit testing. The classical school is called “classical” because it’s how everyone originally approached unit testing and test-driven development. The London school takes root in the programming community in London. The discussion in this chapter about the differences between the classical and London styles lays the foundation for chapter 5, where I cover the topic of mocks and test fragility in detail.

这些观点被称为单元测试的经典学派和伦敦学派。经典学派被称为 “classical”，因为它是每个人最初接触单元测试和测试驱动开发（TDD）的方式。伦敦学派扎根于伦敦的编程社区。本章关于经典和伦敦风格的讨论为第五章奠定了基础，在第五章中我将详细介绍mock 和测试脆弱性的话题。

Let’s start by defining a unit test, with all due caveats and subtleties. This definition is the key to the difference between the classical and London schools.

让我们从定义单元测试开始，包括所有适当的注意事项和微妙之处。这个定义是区分经典和伦敦学派的关键。

## [](#2-1-“单元测试”的定义 "2.1 “单元测试”的定义")2.1 “单元测试”的定义

**The definition of “unit test”**

There are a lot of definitions of a unit test. Stripped of their non-essential bits, the definitions all have the following three most important attributes. A unit test is an automated test that

有很多关于单元测试的定义。剥去其非必要的部分，这些定义都有以下三个最重要的属性。单元测试是一种自动化测试，它

*   Verifies a small piece of code (also known as a unit), 验证一小段代码（也被称为单元）
*   Does it quickly, 迅速完成
*   And does it in an isolated manner. 并以一种隔离的方式进行

The first two attributes here are pretty non-controversial. There might be some dispute as to what exactly constitutes a fast unit test because it’s a highly subjective measure. But overall, it’s not that important. If your test suite’s execution time is good enough for you, it means your tests are quick enough.

这里的前两个属性是相当没有争议的。对于究竟什么是快速的单元测试，可能会有一些争议，因为这是一个非常主观的衡量标准。但总的来说，这并不那么重要。如果你的测试套件的执行时间对你来说足够好，这意味着你的测试足够快。

What people have vastly different opinions about is the third attribute. The isolation issue is the root of the differences between the classical and London schools of unit testing. As you will see in the next section, all other differences between the two schools flow naturally from this single disagreement on what exactly isolation means. I prefer the classical style for the reasons I describe in section 2.3.

人们对第三个属性有截然不同的看法。隔离问题是单元测试的经典学派和伦敦学派之间分歧的根源。如你将在下一节看到的那样，这两个学派之间的所有其他分歧自然都来自于对隔离到底意味着什么这个单一的分歧。我更喜欢古典风格，原因我将在2.3节中阐述。

> **The classical and London schools of unit testing**
> 
> **单元测试的经典学派和伦敦学派**
> 
> The classical approach is also referred to as the Detroit and, sometimes, the classicist approach to unit testing. Probably the most canonical book on the classical school is the one by Kent Beck: Test-Driven Development: By Example (Addison-Wesley Professional, 2002).
> 
> 经典风格也被称为底特律风格，有时也被称为单元测试的经典主义风格。关于经典学派最经典的书可能是 Kent Beck 的那本： Test-Driven Development: By Example (TDD，测试驱动开发).
> 
> The London style is sometimes referred to as mockist. Although the term mockist is widespread, people who adhere to this style of unit testing generally don’t like it, so I call it the London style throughout this book. The most prominent proponents of this approach are Steve Freeman and Nat Pryce. I recommend their book, Growing ObjectOriented Software, Guided by Tests (Addison-Wesley Professional, 2009), as a good source on this subject.
> 
> 伦敦风格有时被称为 mockist。虽然 mockist 这个词很普遍，但坚持这种单元测试风格的人一般都不喜欢，所以我在本书中称它为伦敦风格。这种方法最突出的支持者是 Steve Freeman 和 Nat Pryce。我推荐他们的书《Growing ObjectOriented Software, Guided by Tests》，作为这个主题的一个很好的起源。

### [](#2-1-1-隔离问题：-伦敦学派的观点 "2.1.1 隔离问题： 伦敦学派的观点")2.1.1 隔离问题： 伦敦学派的观点

**The isolation issue: The London take**

What does it mean to verify a piece of code—a unit—in an isolated manner? The London school describes it as isolating the system under test from its collaborators. It means if a class has a dependency on another class, or several classes, you need to replace all such dependencies with test doubles. This way, you can focus on the class under test exclusively by separating its behavior from any external influence.

以隔离的方式验证一段代码–一个单元，这意味着什么？伦敦学派将其描述为将被测系统与它的合作者隔离。这意味着如果一个类对另一个类，或几个类有依赖性，你需要用测试替身来取代所有这些依赖。这样，你就可以把注意力集中在被测类上，把它的行为与任何外部影响分开。

> DEFINITION 定义
> 
> A test double is an object that looks and behaves like its releaseintended counterpart but is actually a simplified version that reduces the complexity and facilitates testing. This term was introduced by Gerard Meszaros in his book, xUnit Test Patterns: Refactoring Test Code (Addison-Wesley, 2007). The name itself comes from the notion of a stunt double in movies.
> 
> 测试替身是一个对象，它看起来和行为都与发布时的对应物一样，但实际上是一个简化的版本，可以降低复杂性并方便测试。这个术语是由 Gerard Meszaros 在他的书《xUnit Test Patterns: Refactoring Test Code》中提出的。这个名字本身来自于电影中特技替身的概念。

Figure 2.1 shows how the isolation is usually achieved. A unit test that would otherwise verify the system under test along with all its dependencies now can do that separately from those dependencies.

图2.1显示了通常是如何实现隔离的。一个单元测试本来是要验证被测系统和它的所有依赖关系的，现在可以脱离这些依赖关系单独进行。

![image-20230409183613683](~/assets/images/unit-testing-2/image-20230409183613683.png)

Figure 2.1 Replacing the dependencies of the system under test with test doubles allows you to focus on verifying the system under test exclusively, as well as split the otherwise large interconnected object graph.

图2.1 用测试替身取代被测系统的依赖关系，可以使你专注于验证被测系统，以及分割原本庞大的相互连接的对象图。

One benefit of this approach is that if the test fails, you know for sure which part of the code base is broken: it’s the system under test. There could be no other suspects, because all of the class’s neighbors are replaced with the test doubles.

这种方法的一个好处是，如果测试失败，你可以肯定地知道代码库的哪一部分被破坏了：是被测系统。不可能有其他的嫌疑人，因为该类的所有邻元素都被替换成了测试用的替身。

Another benefit is the ability to split the object graph—the web of communicating classes solving the same problem. This web may become quite complicated: every class in it may have several immediate dependencies, each of which relies on dependencies of their own, and so on. Classes may even introduce circular dependencies, where the chain of dependency eventually comes back to where it started.

另一个好处是能够分割对象图–解决同一问题的通信类的网络。这个网络可能会变得相当复杂：其中的每一个类都可能有几个直接的依赖关系，每一个都依赖于它们自己的依赖关系，等等。类甚至可以引入循环依赖关系，即依赖链最终会回到它的起点。

Trying to test such an interconnected code base is hard without test doubles. Pretty much the only choice you are left with is re-creating the full object graph in the test, which might not be a feasible task if the number of classes in it is too high.

试图测试这样一个相互关联的代码库，如果没有测试替身，是很难的。几乎你唯一的选择就是在测试中重新创建完整的对象图，如果其中的类的数量太多，这可能不是一个可行的任务。

With test doubles, you can put a stop to this. You can substitute the immediate dependencies of a class; and, by extension, you don’t have to deal with the dependencies of those dependencies, and so on down the recursion path. You are effectively breaking up the graph—and that can significantly reduce the amount of preparations you have to do in a unit test.

有了测试替身，你就可以停止这种做法了。你可以替代一个类的直接依赖关系；而且，推而广之，你不必处理这些依赖关系的依赖关系，并以此类推，沿着递归路径。你正在有效地分解图–这可以大大减少你在单元测试中所做的准备工作的数量。

And let’s not forget another small but pleasant side benefit of this approach to unit test isolation: it allows you to introduce a project-wide guideline of testing only one class at a time, which establishes a simple structure in the whole unit test suite. You no longer have to think much about how to cover your code base with tests. Have a class? Create a corresponding class with unit tests! Figure 2.2 shows how it usually looks.

我们不要忘记这种单元测试隔离方法的另一个小但令人愉快的附带好处：它允许你在整个项目中引入一次只测试一个类的准则，这在整个单元测试套件中建立了一个简单的结构。你不再需要过多考虑如何用测试来覆盖你的代码库。有一个类？用单元测试创建一个相应的类吧! 图 2.2 显示了它通常的样子。

![image-20230409183714141](~/assets/images/unit-testing-2/image-20230409183714141.png)

Figure 2.2 Isolating the class under test from its dependencies helps establish a simple test suite structure: one class with tests for each class in the production code.

图 2.2 将被测类与它的依赖关系隔离开来，有助于建立一个简单的测试套件结构：一个类与生产代码中的每个类的测试。

Let’s now look at some examples. Since the classical style probably looks more familiar to most people, I’ll show sample tests written in that style first and then rewrite them using the London approach.

现在让我们看看一些例子。由于经典学派的风格对大多数人来说可能更熟悉，我将首先展示用这种风格编写的测试样本，然后用伦、伦敦学派方法重写它们。

Let’s say that we operate an online store. There’s just one simple use case in our sample application: a customer can purchase a product. When there’s enough inventory in the store, the purchase is deemed to be successful, and the amount of the product in the store is reduced by the purchase’s amount. If there’s not enough product, the purchase is not successful, and nothing happens in the store.

假设我们经营一家在线商店。在我们的示例应用进程中只有一个简单的用例：客户可以购买产品。当商店中有足够的库存时，购买被视为成功，商店中的产品数量将减去购买的数量。如果没有足够的产品，则购买不成功，商店中不会发生任何事情。

Listing 2.1 shows two tests verifying that a purchase succeeds only when there’s enough inventory in the store. The tests are written in the classical style and use the typical three-phase sequence: arrange, act, and assert (AAA for short—I talk more about this sequence in chapter 3).

清单 2.1 显示了两个测试，验证只有当商店里有足够的库存时购买才会成功。这些测试是以经典学派的风格编写的，并使用了典型的三阶段顺序：arrange（安排/准备）、act（行动/执行）和 assert（断言）（简称AAA，我在第3章中会更多地讨论这个顺序）。

Listing 2.1 Tests written using the classical style of unit testing 清单 2.1 使用经典的单元测试风格编写的测试

![image-20230409183807626](~/assets/images/unit-testing-2/image-20230409183807626.png)

As you can see, the arrange part is where the tests make ready all dependencies and the system under test. The call to customer.Purchase() is the act phase, where you exercise the behavior you want to verify. The assert statements are the verification stage, where you check to see if the behavior led to the expected results.

正如你所看到的，准备部分是测试准备好所有的依赖关系和被测系统的地方。对 customer.Purchase() 的调用是执行阶段，在这里你执行你想要验证的行为。assert 语句是验证阶段，在这里你检查行为是否达到了预期的结果。

During the arrange phase, the tests put together two kinds of objects: the system under test (SUT) and one collaborator. In this case, Customer is the SUT and Store is the collaborator. We need the collaborator for two reasons:

在准备阶段，测试将两种对象放在一起：被测系统（SUT）和一个合作者。在这种情况下，Customer 是 SUT，Store 是合作者。我们需要合作者有两个原因：

*   To get the method under test to compile, because customer.Purchase() requires a Store instance as an argument 为了使被测方法能够编译，因为 customer.Purchase() 需要一个 Store 实例作为参数。
    
*   For the assertion phase, since one of the results of customer.Purchase() is a potential decrease in the product amount in the store 对于断言阶段，因为 customer.Purchase() 的结果之一是商店里的产品数量可能会减少
    

Product.Shampoo and the numbers 5 and 15 are constants.

Product.Shampoo 和 数字 5 和 15 是常数。

> DEFINITION
> 
> A method under test (MUT) is a method in the SUT called by the test. The terms MUT and SUT are often used as synonyms, but normally, MUT refers to a method while SUT refers to the whole class.
> 
> 被测方法（MUT）是 SUT 中被测试调用的一个方法。术语 MUT 和 SUT 经常被用作同义词，但通常，MUT 指的是一个方法，而 SUT 指的是整个类。

This code is an example of the classical style of unit testing: the test doesn’t replace the collaborator (the Store class) but rather uses a production-ready instance of it. One of the natural outcomes of this style is that the test now effectively verifies both Customer and Store, not just Customer. Any bug in the inner workings of Store that affects Customer will lead to failing these unit tests, even if Customer still works correctly. The two classes are not isolated from each other in the tests.

这段代码是单元测试的经典学派风格的一个例子：测试并不替换合作者（Store 类），而是使用它的一个生产就绪的实例。这种风格的自然结果之一是，测试现在有效地验证了 Customer 和 Store，而不仅仅是 Customer。Store 内部工作中的任何影响到 Customer 的错误都会导致这些单元测试的失败，即使 Customer 仍然工作正常。这两个类在测试中并不是相互隔离的。

Let’s now modify the example toward the London style. I’ll take the same tests and replace the Store instances with test doubles—specifically, mocks.

现在让我们把这个例子修改为伦敦学派风格。我将采用相同的测试，并将 Store 的实例替换为测试替身–具体来说，就是模拟（mocks）。

I use [Moq](https://github.com/moq/moq4) as the mocking framework, but you can find several equally good alternatives, such as \[NSubstitute\]([https://github.com/](https://github.com/) nsubstitute/NSubstitute). All object-oriented languages have analogous frameworks. For instance, in the Java world, you can use Mockito, JMock, or EasyMock.

我使用 [Moq](https://github.com/moq/moq4)作为 mocking 框架，但你可以找到几个同样好的替代品，如 [NSubstitute](https://github.com/nsubstitute/NSubstitute)。所有面向对象的语言都有类似的框架。例如，在Java世界中，你可以使用 Mockito、JMock 或 EasyMock。

> DEFINITION
> 
> A mock is a special kind of test double that allows you to examine interactions between the system under test and its collaborators.
> 
> mock 是一种特殊的测试替身，它允许你检查被测系统和其合作者之间的交互。

We’ll get back to the topic of mocks, stubs, and the differences between them in later chapters. For now, the main thing to remember is that mocks are a subset of test doubles. People often use the terms test double and mock as synonyms, but technically, they are not (more on this in chapter 5):

我们将在后面的章节中再讨论 mock、stubs 的话题，以及它们之间的区别。现在，主要要记住的是，mocks 是测试替身的一个子集。人们经常把测试替身和模拟作为同义词使用，但从技术上讲，它们不是（在第5章有更多的介绍）：

*   Test double is an overarching term that describes all kinds of non-productionready, fake dependencies in a test. 测试替身是一个总的术语，它描述了测试中所有种类的非生产就绪的、虚假的依赖。
*   Mock is just one kind of such dependencies. Mock只是这种依赖的一种。

The next listing shows how the tests look after isolating Customer from its collaborator, Store.

下一个列表显示了将 Customer 与它的合作者 Store 隔离后的测试情况。

Listing 2.2 Tests written using the London style of unit testing

```csharp
1   [Fact]
2   public void Purchase_succeeds_when_enough_inventory()
3   {
4   	// Arrange
5   	var storeMock = new Mock<IStore>();
6   	storeMock
7   		.Setup(x => x.HasEnoughInventory(Product.Shampoo, 5))
8   		.Returns(true);
9   	var customer = new Customer();
10  	// Act
11  	bool success = customer.Purchase(
12  	storeMock.Object, Product.Shampoo, 5);
13  	// Assert
14  	Assert.True(success);
15  	storeMock.Verify(
16  		x => x.RemoveInventory(Product.Shampoo, 5),
17  		Times.Once);
18  }
19  [Fact]
20  public void Purchase_fails_when_not_enough_inventory()
21  {
22  	// Arrange
23  	var storeMock = new Mock<IStore>();
24  	storeMock
25  		.Setup(x => x.HasEnoughInventory(Product.Shampoo, 5))
26  		.Returns(false);
27  	var customer = new Customer();
28  	// Act
29  	bool success = customer.Purchase(
30  	storeMock.Object, Product.Shampoo, 5);
31  	// Assert
32  	Assert.False(success);
33  	storeMock.Verify(
34  		x => x.RemoveInventory(Product.Shampoo, 5),
35  		Times.Never);
36  }
```

Note how different these tests are from those written in the classical style. In the arrange phase, the tests no longer instantiate a production-ready instance of Store but instead create a substitution for it, using Moq’s built-in class Mock.

请注意这些测试与经典风格的测试有多大不同。在准备阶段，测试不再实例化一个生产就绪的 Store 实例，而是使用 Moq 的内置类 Mock 为其创建一个替代物。

Furthermore, instead of modifying the state of Store by adding a shampoo inventory to it, we directly tell the mock how to respond to calls to HasEnoughInventory(). The mock reacts to this request the way the tests need, regardless of the actual state of Store. In fact, the tests no longer use Store—we have introduced an IStore interface and are mocking that interface instead of the Store class.

此外，我们不是通过添加 shampoo 库存来修改 Store 的状态，而是直接告诉 mock 如何响应对 HasEnoughInventory() 的调用。无论Store 的实际状态如何，mock 都会以测试需要的方式对该请求做出反应。事实上，测试不再使用 Store–我们已经引入了一个 IStore 接口，并对该接口进行了模拟，而不是 Store 类。

In chapter 8, I write in detail about working with interfaces. For now, just make a note that interfaces are required for isolating the system under test from its collaborators. (You can also mock a concrete class, but that’s an anti-pattern; I cover this topic in chapter 11.)

在第8章中，我将详细介绍如何使用接口。现在，只要注意到接口是将被测系统与合作者隔离的必要条件。(你也可以模拟一个具体的类，但这是一种反模式；我在第11章中介绍了这个话题)。

The assertion phase has changed too, and that’s where the key difference lies. We still check the output from customer.Purchase as before, but the way we verify that the customer did the right thing to the store is different. Previously, we did that by asserting against the store’s state. Now, we examine the interactions between Customer and Store: the tests check to see if the customer made the correct call on the store. We do this by passing the method the customer should call on the store (x.RemoveInventory) as well as the number of times it should do that. If the purchases succeeds, the customer should call this method once (Times.Once). If the purchases fails, the customer shouldn’t call it at all (Times.Never).

断言阶段也发生了变化，这就是关键的区别所在。我们仍然像以前一样检查 customer.Purchase 的输出，但我们验证客户对商店所做的事情是否正确的方式是不同的。以前，我们通过对商店的状态进行断言来做到这一点。现在，我们检查客户和商店之间的交互：测试检查客户是否对商店进行了正确的调用。我们通过传递客户应该在商店上调用的方法（x.RemoveInventory）以及它应该做的次数来做到这一点。如果购买成功，客户应该调用这个方法一次（Times.Once）。如果购买失败，客户就不应该调用该方法（Times.Never）。

### [](#2-1-2-隔离问题：-经典学派的观点 "2.1.2 隔离问题： 经典学派的观点")2.1.2 隔离问题： 经典学派的观点

**The isolation issue: The classical take**

To reiterate, the London style approaches the isolation requirement by segregating the piece of code under test from its collaborators with the help of test doubles: specifically, mocks. Interestingly enough, this point of view also affects your standpoint on what constitutes a small piece of code (a unit). Here are all the attributes of a unit test once again:

重申一下，伦敦学派风格的做法是，在测试替身的帮助下，将被测试的这段代码与它的合作者隔离开来，特别是模拟。有趣的是，这种观点也会影响你对什么是一小段代码（一个单元）的看法。下面是单元测试的所有属性，再一次列出：

*   A unit test verifies a small piece of code (a unit), 一个单元测试验证一小段代码（一个单元）
*   Does it quickly, 迅速完成
*   And does it in an isolated manner. 并以一种隔离的方式进行。

In addition to the third attribute leaving room for interpretation, there’s some room in the possible interpretations of the first attribute as well. How small should a small piece of code be? As you saw from the previous section, if you adopt the position of isolating every individual class, then it’s natural to accept that the piece of code under test should also be a single class, or a method inside that class. It can’t be more than that due to the way you approach the isolation issue. In some cases, you might test a couple of classes at once; but in general, you’ll always strive to maintain this guideline of unit testing one class at a time.

除了第三个属性有解释的余地外，第一个属性也有一些可能的解释空间。一段小的代码应该有多小？正如你在上一节中所看到的，如果你采取隔离每一个单独的类的立场，那么很自然地接受被测试的那段代码也应该是一个单独的类，或者该类中的一个方法。由于你处理隔离问题的方式，它不可能超过这个范围。在某些情况下，你可能会同时测试几个类；但总的来说，你会一直努力保持这种一次测试一个类的单元测试准则。

As I mentioned earlier, there’s another way to interpret the isolation attribute— the classical way. In the classical approach, it’s not the code that needs to be tested in an isolated manner. Instead, unit tests themselves should be run in isolation from each other. That way, you can run the tests in parallel, sequentially, and in any order, whatever fits you best, and they still won’t affect each other’s outcome.

正如我前面提到的，还有另一种方式来解释隔离属性–经典学派的方式。在经典学派的方式中，需要以隔离的方式测试的不是代码。相反，单元测试本身应该在相互隔离的情况下运行。这样，你可以平行地、顺序地、以任何顺序地运行测试，只要是最适合你的，它们仍然不会影响彼此的结果。

Isolating tests from each other means it’s fine to exercise several classes at once as long as they all reside in the memory and don’t reach out to a shared state, through which the tests can communicate and affect each other’s execution context. Typical examples of such a shared state are out-of-process dependencies—the database, the file system, and so on.

互相隔离测试意味着可以同时校验几个类，只要它们都驻留在内存中，并且不接触到共享状态，通过共享状态，测试可以互相通信并影响对方的执行环境。这种共享状态的典型例子是进程外的依赖–数据库、文件系统，等等。

For instance, one test could create a customer in the database as part of its arrange phase, and another test would delete it as part of its own arrange phase, before the first test completes executing. If you run these two tests in parallel, the first test will fail, not because the production code is broken, but rather because of the interference from the second test.

例如，一个测试可以在数据库中创建一个客户，作为其准备阶段的一部分，而另一个测试将删除它，作为其自己准备阶段的一部分，在第一个测试完成执行之前。如果你平行运行这两个测试，第一个测试会失败，不是因为生产代码被破坏，而是因为第二个测试的干扰。

> **Shared, private, and out-of-process dependencies** 共享的、私有的和进程外的依赖关系
> 
> A shared dependency is a dependency that is shared between tests and provides means for those tests to affect each other’s outcome. A typical example of shared dependencies is a static mutable field. A change to such a field is visible across all unit tests running within the same process. A database is another typical example of a shared dependency.
> 
> 共享依赖是指测试之间共享的依赖，并为这些测试提供影响彼此结果的手段。一个典型的共享依赖的例子是一个静态可变的字段。对这样一个字段的改变在同一进程中运行的所有单元测试中是可见的。数据库是另一个共享依赖的典型例子。
> 
> A private dependency is a dependency that is not shared.
> 
> 私有依赖是一种不共享的依赖。
> 
> An out-of-process dependency is a dependency that runs outside the application’s execution process; it’s a proxy to data that is not yet in the memory. An out-of-process dependency corresponds to a shared dependency in the vast majority of cases, but not always. For example, a database is both out-of-process and shared. But if you launch that database in a Docker container before each test run, that would make this dependency out-of-process but not shared, since tests no longer work with the same instance of it. Similarly, a read-only database is also out-of-process but not shared, even if it’s reused by tests. Tests can’t mutate data in such a database and thus can’t affect each other’s outcome.
> 
> 进程外依赖是在应用程序执行过程之外运行的依赖；它是对尚未在内存中的数据的代理。在绝大多数情况下，进程外依赖与共享依赖相对应，但并非总是如此。例如，一个数据库既是进程外的又是共享的。但如果你在每次测试运行前在 Docker 容器中启动该数据库，这将使这个依赖成为进程外的，但不是共享的，因为测试不再与它的同一实例一起工作。同样，一个只读的数据库也是进程外的，但不是共享的，即使它被测试重复使用。测试不能改变这种数据库中的数据，因此不能影响彼此的结果。

This take on the isolation issue entails a much more modest view on the use of mocks and other test doubles. You can still use them, but you normally do that for only those dependencies that introduce a shared state between tests. Figure 2.3 shows how it looks.

这种对隔离问题的看法需要对 mock 和其他测试替身的使用有一个更温和的看法。你仍然可以使用它们，但你通常只对那些在测试之间引入共享状态的依赖关系使用。图 2.3 显示了它的样子。

![image-20230409185813301](~/assets/images/unit-testing-2/image-20230409185813301.png)

Figure 2.3 Isolating unit tests from each other entails isolating the class under test from shared dependencies only. Private dependencies can be kept intact.

图2.3 单元测试之间的隔离，需要将被测类与共享的依赖隔离。私有的依赖可以保持不变。

Note that shared dependencies are shared between unit tests, not between classes under test (units). In that sense, a singleton dependency is not shared as long as you are able to create a new instance of it in each test. While there’s only one instance of a singleton in the production code, tests may very well not follow this pattern and not reuse that singleton. Thus, such a dependency would be private.

请注意，共享依赖是在单元测试之间共享，而不是在被测类（单元）之间共享。在这个意义上，只要你能在每个测试中创建一个新的实例，那么单子依赖就不是共享的。虽然在生产代码中只有一个单独的实例，但测试很可能不遵循这种模式，不重用这个单例。因此，这样的依赖将是私有的。

For example, there’s normally only one instance of a configuration class, which is reused across all production code. But if it’s injected into the SUT the way all other dependencies are, say, via a constructor, you can create a new instance of it in each test; you don’t have to maintain a single instance throughout the test suite. You can’t create a new file system or a database, however; they must be either shared between tests or substituted away with test double.

例如，通常只有一个配置类的实例，它在所有生产代码中被重用。但是，如果它被注入到 SUT 中，就像所有其他的依赖一样，例如，通过一个构造函数，你可以在每个测试中创建一个新的实例；你不必在整个测试套件中维护一个实例。然而，你不能创建一个新的文件系统或数据库；它们必须在测试之间共享，或用测试替身。

> **Shared vs. volatile dependencies** 共享的与不稳定的依赖
> 
> Another term has a similar, yet not identical, meaning: volatile dependency. I recommend Dependency Injection: Principles, Practices, Patterns by Steven van Deursen and Mark Seemann (Manning Publications, 2018) as a go-to book on the topic of dependency management.
> 
> 另一个术语有类似的，但不完全相同的意思：不稳定的依赖。我推荐 Steven van Deursen 和 Mark Seemann的《依赖注入：原则、实践、模式》，作为依赖管理主题的首选书籍。
> 
> A volatile dependency is a dependency that exhibits one of the following properties:
> 
> 一个不稳定的依赖是一个表现出以下属性之一的依赖：
> 
> *   It introduces a requirement to set up and configure a runtime environment in addition to what is installed on a developer’s machine by default. Databases and API services are good examples here. They require additional setup and are not installed on machines in your organization by default. 除了默认安装在开发者机器上的东西之外，它还引入了设置和配置运行时环境的要求。数据库和 API 服务就是很好的例子。它们需要额外的设置，而且默认情况下不会安装在你的组织中的机器上。
> *   It contains nondeterministic behavior. An example would be a random number generator or a class returning the current date and time. These dependencies are non-deterministic because they provide different results on each invocation. 它包含不确定的行为。一个例子是一个随机数生成器或一个返回当前日期和时间的类。这些依赖关系是不确定性的，因为它们在每次调用时提供不同的结果。
> 
> As you can see, there’s an overlap between the notions of shared and volatile dependencies. For example, a dependency on the database is both shared and volatile. But that’s not the case for the file system. The file system is not volatile because it is installed on every developer’s machine and it behaves deterministically in the vast majority of cases. Still, the file system introduces a means by which the unit tests can interfere with each other’s execution context; hence it is shared. Likewise, a random number generator is volatile, but because you can supply a separate instance of it to each test, it isn’t shared.
> 
> 正如你所看到的，共享依赖和不稳定依赖的概念有重叠之处。例如，对数据库的依赖既是共享的又是不稳定的。但对于文件系统来说，情况并非如此。文件系统不是不稳定的，因为它被安装在每个开发人员的机器上，而且在绝大多数情况下它的行为是确定的。然而，文件系统引入了一种手段，单元测试可以干扰彼此的执行环境；因此它是共享的。同样，随机数发生器是不稳定的，但是因为你可以为每个测试提供一个单独的实例，所以它不是共享的。

Another reason for substituting shared dependencies is to increase the test execution speed. Shared dependencies almost always reside outside the execution process, while private dependencies usually don’t cross that boundary. Because of that, calls to shared dependencies, such as a database or the file system, take more time than calls to private dependencies. And since the necessity to run quickly is the second attribute of the unit test definition, such calls push the tests with shared dependencies out of the realm of unit testing and into the area of integration testing. I talk more about integration testing later in this chapter.

替代共享依赖的另一个原因是提高测试执行速度。共享的依赖关系几乎总是在执行过程之外，而私有的依赖通常不会跨越这个边界。正因为如此，对共享依赖的调用，如数据库或文件系统，要比对私有依赖的调用花费更多时间。由于快速运行的必要性是单元测试定义的第二个属性，这种调用将共享依赖的测试从单元测试的领域推到了集成测试的领域。我在本章后面会更多地谈及集成测试。

This alternative view of isolation also leads to a different take on what constitutes a unit (a small piece of code). A unit doesn’t necessarily have to be limited to a class.

这种对隔离的另一种看法也导致了对单元（一小段代码）构成的不同看法。一个单元不一定非要局限于一个类。

You can just as well unit test a group of classes, as long as none of them is a shared dependency.

你也可以对一组类进行单元测试，只要它们中没有一个是共享的依赖关系。

## [](#2-2-单元测试的经典和伦敦学派 "2.2 单元测试的经典和伦敦学派")2.2 单元测试的经典和伦敦学派

**The classical and London schools of unit testing**

As you can see, the root of the differences between the London and classical schools is the isolation attribute. The London school views it as isolation of the system under test from its collaborators, whereas the classical school views it as isolation of unit tests themselves from each other.

正如你所看到的，伦敦学派和经典学派之间差异的根源在于隔离属性。伦敦学派认为它是被测系统与合作者的隔离，而经典学派则认为它是单元测试本身与其他的隔离。

This seemingly minor difference has led to a vast disagreement about how to approach unit testing, which, as you already know, produced the two schools of thought. Overall, the disagreement between the schools spans three major topics:

这个看似微小的差异导致了关于如何进行单元测试的巨大分歧，正如你已经知道的，这产生了两个学派。总的来说，这两个学派之间的分歧跨越了三个主主题：

*   The isolation requirement 隔离的要求
*   What constitutes a piece of code under test (a unit) 什么是被测试的一段代码（单元）？
*   Handling dependencies 处理依赖

Table 2.1 sums it all up.

表2.1总结了这一切。

Table 2.1 The differences between the London and classical schools of unit testing, summed up by the approach to isolation, the size of a unit, and the use of test doubles

表2.1 单元测试的伦敦学派和经典学派之间的差异，由隔离的方法、单元的大小和测试替身的使用情况总结而来

Isolation of

A unit is

Uses test doubles for

London school

Units

A class

All but immutable dependencies

Classical school

Unit tests

A class or a set of classes

Shared dependencies

### [](#2-2-1-经典学派和伦敦学派如何处理依赖 "2.2.1 经典学派和伦敦学派如何处理依赖")2.2.1 经典学派和伦敦学派如何处理依赖

**How the classical and London schools handle dependencies**

Note that despite the ubiquitous use of test doubles, the London school still allows for using some dependencies in tests as-is. The litmus test here is whether a dependency is mutable. It’s fine not to substitute objects that don’t ever change— immutable objects.

请注意，尽管测试替身的使用无处不在，伦敦学派仍然允许在测试中原样使用一些依赖关系。这里的准则是一个依赖是否是可变的。不替代那些永远不会改变的对象–不可变的对象是很好的。

And you saw in the earlier examples that, when I refactored the tests toward the London style, I didn’t replace the Product instances with mocks but rather used the real objects, as shown in the following code (repeated from listing 2.2 for your convenience)

你在前面的例子中看到，当我按照伦敦风格重构测试时，我没有用模拟来替换 Product 实例，而是使用真实的对象，如下面的代码所示（为了你的方便，从列表2.2重复）。

```csharp
1   [Fact]
2   public void Purchase_fails_when_not_enough_inventory()
3   {
4   	// Arrange
5   	var storeMock = new Mock<IStore>();
6   	storeMock
7   		.Setup(x => x.HasEnoughInventory(Product.Shampoo, 5))
8   		.Returns(false);
9   	var customer = new Customer();
10      // Act
11  	bool success = customer.Purchase(storeMock.Object, Product.Shampoo, 5);
12  	// Assert
13  	Assert.False(success);
14  	storeMock.Verify(
15  		x => x.RemoveInventory(Product.Shampoo, 5),
16  		Times.Never);
17  }
```

Of the two dependencies of Customer, only Store contains an internal state that can change over time. The Product instances are immutable (Product itself is a C# enum). Hence I substituted the Store instance only.

在 Customer 的两个依赖关系中，只有 Store 包含一个可以随时间变化的内部状态。Product 实例是不可改变的（Product 本身是一个 C# 枚举）。因此我只替换了 Store 实例。

It makes sense, if you think about it. You wouldn’t use a test double for the 5 number in the previous test either, would you? That’s because it is also immutable— you can’t possibly modify this number. Note that I’m not talking about a variable containing the number, but rather the number itself. In the statement RemoveInventory(Product.Shampoo, 5), we don’t even use a variable; 5 is declared right away. The same is true for Product.Shampoo.

如果你仔细想想，这是有道理的。在前面的测试中，你也不会用一个测试替身来表示 5 的数字，对吗？那是因为它也是不可变的–你不可能修改这个数字。注意，我说的不是包含这个数字的变量，而是这个数字本身。在 RemoveInventory(Product.Shampoo, 5) 这个语句中，我们甚至没有使用一个变量；5 被立即声明。Product.Shampoo 的情况也是如此。

Such immutable objects are called value objects or values. Their main trait is that they have no individual identity; they are identified solely by their content. As a corollary, if two such objects have the same content, it doesn’t matter which of them you’re working with: these instances are interchangeable. For example, if you’ve got two 5 integers, you can use them in place of one another. The same is true for the products in our case: you can reuse a single Product.Shampoo instance or declare several of them—it won’t make any difference. These instances will have the same content and thus can be used interchangeably.

这种不可改变的对象被称为值对象或值。它们的主要特征是它们没有单独的标识；它们只通过其内容来识别。作为一个推论，如果两个这样的对象有相同的内容，你用哪个对象并不重要：这些实例是可以互换的。例如，如果你有两个整数 5，你可以用它们来代替对方。在我们的案例中，product 也是如此：你可以重复使用一个 Product.Shampoo 实例或者声明几个实例–这不会有任何区别。这些实例将有相同的内容，因此可以互换使用。

Note that the concept of a value object is language-agnostic and doesn’t require a particular programming language or framework. You can read more about value objects in my article “Entity vs. Value Object: The ultimate list of differences” at [http://mng.bz/KE9O](http://mng.bz/KE9O).

请注意，值对象的概念是不分语言的，不需要特定的编程语言或框架。你可以在我的文章《实体与价值对象： 差异终极清单》，网址是 [http://mng.bz/KE9O。](http://mng.bz/KE9O%E3%80%82)

Figure 2.4 shows the categorization of dependencies and how both schools of unit testing treat them. A dependency can be either shared or private. A private dependency, in turn, can be either mutable or immutable. In the latter case, it is called a value object. For example, a database is a shared dependency—its internal state is shared across all automated tests (that don’t replace it with a test double). A Store instance is a private dependency that is mutable. And a Product instance (or an instance of a number 5, for that matter) is an example of a private dependency that is immutable—a value object. All shared dependencies are mutable, but for a mutable dependency to be shared, it has to be reused by tests.

图 2.4 显示了依赖的分类以及两种单元测试流派如何对待它们。依赖可以是共享的，也可以是私有的。而一个私有的依赖可以是可变的，也可以是不可变的。在后一种情况下，它被称为一个值对象。例如，数据库是一个共享的依赖关系–它的内部状态在所有的自动测试中都是共享的（没有用测试替身替换它）。一个 Store 实例是一个私有的依赖关系，它是可变的。而 Product 实例（或数字 5 的实例，对于这个问题）是一个私有依赖的例子，它是不可改变的–值对象。所有共享的依赖都是可变的，但是要使可变的依赖被共享，它必须被测试重用。

![image-20230409190415686](~/assets/images/unit-testing-2/image-20230409190415686-1725861610072-1.png)

Figure 2.4 The hierarchy of dependencies. The classical school advocates for replacing shared dependencies with test doubles. The London school advocates for the replacement of private dependencies as well, as long as they are mutable.

图2.4 依赖的层次结构。经典学派主张用测试替身来取代共享依赖关系。伦敦学派主张也要替换私有的依赖，只要它们是可变的。

I’m repeating table 2.1 with the differences between the schools for your convenience.

为了方便起见，我在表2.1中重复了各流派之间的差异。

Isolation of

A unit is

Uses test doubles for

London school

Units

A class

All but immutable dependencies

Classical school

Unit tests

A class or a set of classes

Shared dependencies

> **Collaborator vs. dependency** 合作者与依赖
> 
> A collaborator is a dependency that is either shared or mutable. For example, a class providing access to the database is a collaborator since the database is a shared dependency. Store is a collaborator too, because its state can change over time.
> 
> 合作者是一个共享或可变的依赖。例如，一个提供对数据库访问的类是一个合作者，因为数据库是一个共享的依赖关系。Store 也是一个合作者，因为它的状态可以随时间变化。
> 
> Product and number 5 are also dependencies, but they’re not collaborators. They’re values or value objects.
> 
> Product 和数字 5 也是依赖关系，但它们不是合作者。它们是值或值对象。
> 
> A typical class may work with dependencies of both types: collaborators and values. Look at this method call:
> 
> 一个典型的类可能与两种类型的依赖关系一起工作：合作者和值。看看这个方法调用：
> 
> ```csharp
> 1   customer.Purchase(store, Product.Shampoo, 5)
> ```
> 
> Here we have three dependencies. One of them (store) is a collaborator, and the other two (Product.Shampoo, 5) are not.
> 
> 这里我们有三个依赖。其中一个（store）是合作者，而另外两个（Product.Shampoo, 5）不是。

And let me reiterate one point about the types of dependencies. Not all out-of-process dependencies fall into the category of shared dependencies. A shared dependency almost always resides outside the application’s process, but the opposite isn’t true (see figure 2.5). In order for an out-of-process dependency to be shared, it has to provide means for unit tests to communicate with each other. The communication is done through modifications of the dependency’s internal state. In that sense, an immutable out-of-process dependency doesn’t provide such a means. The tests simply can’t modify anything in it and thus can’t interfere with each other’s execution context.

让我重申关于依赖类型的一点。并非所有进程外的依赖关系都属于共享依赖关系的范畴。一个共享的依赖几乎总是驻扎在应用程序的进程之外，但事实并非如此（见图 2.5）。为了使进程外的依赖被共享，它必须为单元测试提供相互通信的方法。这种通信是通过修改依赖的内部状态来完成的。在这个意义上，不可变的进程外依赖不提供这样的手段。测试不能修改其中的任何东西，因此不能干扰彼此的执行环境。

![image-20230409201951138](~/assets/images/unit-testing-2/image-20230409201951138.png)

Figure 2.5 The relation between shared and out-of-process dependencies. An example of a dependency that is shared but not out-of-process is a singleton (an instance that is reused by all tests) or a static field in a class. A database is shared and out-of-process—it resides outside the main process and is mutable. A read-only API is out-of-process but not shared, since tests can’t modify it and thus can’t affect each other’s execution flow.

图 2.5 共享和进程外依赖之间的关系。一个共享但不是进程外的依赖的例子是一个单例（所有测试都重复使用的实例）或一个类中的静态字段。数据库是共享的和进程外的–它驻留在主进程之外并且是可变的。一个只读的 API 是进程外的，但不是共享的，因为测试不能修改它，因此不能影响彼此的执行流程。

For example, if there’s an API somewhere that returns a catalog of all products the organization sells, this isn’t a shared dependency as long as the API doesn’t expose the functionality to change the catalog. It’s true that such a dependency is volatile and sits outside the application’s boundary, but since the tests can’t affect the data it returns, it isn’t shared. This doesn’t mean you have to include such a dependency in the testing scope. In most cases, you still need to replace it with a test double to keep the test fast. But if the out-of-process dependency is quick enough and the connection to it is stable, you can make a good case for using it as-is in the tests.

例如，如果某个地方有一个 API，它返回该组织销售的所有产品的目录，只要该 API 不暴露改变目录的功能，这就不是一个共享的依赖性。诚然，这样的依赖是不稳定的，位于应用程序的边界之外，但由于测试不能影响它所返回的数据，所以它不是共享的。这并不意味着你必须在测试范围内包括这样的依赖。在大多数情况下，你仍然需要用一个测试替身来代替它，以保持测试的快速性。但是，如果进程外依赖项足够快并且与它的连接是稳定的，则可以在测试中按原样使用它。

Having that said, in this book, I use the terms shared dependency and out-of-process dependency interchangeably unless I explicitly state otherwise. In real-world projects, you rarely have a shared dependency that isn’t out-of-process. If a dependency is inprocess, you can easily supply a separate instance of it to each test; there’s no need to share it between tests. Similarly, you normally don’t encounter an out-of-process dependency that’s not shared. Most such dependencies are mutable and thus can be modified by tests.

尽管如此，在本书中，除非我明确说明，否则我将共享依赖和进程外依赖这两个术语互换使用。在现实世界的项目中，你很少有一个共享的依赖不是进程外的。如果一个依赖是进程中的，你可以很容易地为每个测试提供一个单独的实例；没有必要在测试之间共享它。同样地，你通常不会遇到不共享的进程外依赖关系。大多数这样的依赖是可变的，因此可以被测试修改。

With this foundation of definitions, let’s contrast the two schools on their merits.

有了这个定义的基础，让我们对比一下这两个流派的优点。

## [](#2-3-对比经典和伦敦学派的单元测试 "2.3 对比经典和伦敦学派的单元测试")2.3 对比经典和伦敦学派的单元测试

**Contrasting the classical and London schools of unit testing**

To reiterate, the main difference between the classical and London schools is in how they treat the isolation issue in the definition of a unit test. This, in turn, spills over to the treatment of a unit—the thing that should be put under test—and the approach to handling dependencies.

重申一下，经典学派和伦敦学派的主要区别在于他们如何处理单元测试定义中的隔离问题。这反过来又涉及到单元的处理–应该被测试的东西，以及处理依赖的方法。

As I mentioned previously, I prefer the classical school of unit testing. It tends to produce tests of higher quality and thus is better suited for achieving the ultimate goal of unit testing, which is the sustainable growth of your project. The reason is fragility: tests that use mocks tend to be more brittle than classical tests (more on this in chapter 5). For now, let’s take the main selling points of the London school and evaluate them one by one.

正如我之前提到的，我更喜欢单元测试的经典学派。它倾向于产生更高质量的测试，因此更适合于实现单元测试的最终目标，也就是项目的可持续增长。原因是脆弱性：使用 mock 的测试往往比经典学派的测试更脆弱（这一点在第五章有更多介绍）。现在，让我们把伦敦学派的主要卖点逐一评估一下。

The London school’s approach provides the following benefits:

伦敦学派的方法提供了以下好处：

*   Better granularity. The tests are fine-grained and check only one class at a time. 更好的颗粒度。测试是细粒度的，一次只检查一个类。
*   It’s easier to unit test a larger graph of interconnected classes. Since all collaborators are replaced by test doubles, you don’t need to worry about them at the time of writing the test. 对一个较大的相互连接的类的图进行单元测试更容易。因为所有的合作者都被测试替身所取代，你不需要在写测试的时候担心他们。
*   If a test fails, you know for sure which functionality has failed. Without the class’s collaborators, there could be no suspects other than the class under test itself. Of course, there may still be situations where the system under test uses a value object and it’s the change in this value object that makes the test fail. But these cases aren’t that frequent because all other dependencies are eliminated in tests. 如果测试失败了，你可以肯定地知道哪个功能失败了。如果没有类的协作者，除了被测试的类本身，就不可能有其他嫌疑人。当然，仍然可能有这样的情况：被测系统使用了一个值对象，正是这个值对象的变化使测试失败。但这些情况并不频繁，因为所有其他的依赖关系在测试中都被消除了。

### [](#2-3-1-一次测试一个类 "2.3.1 一次测试一个类")2.3.1 一次测试一个类

**Unit testing one class at a time**

The point about better granularity relates to the discussion about what constitutes a unit in unit testing. The London school considers a class as such a unit. Coming from an object-oriented programming background, developers usually regard classes as the atomic building blocks that lie at the foundation of every code base. This naturally leads to treating classes as the atomic units to be verified in tests, too. This tendency is understandable but misleading.

关于更好的颗粒度的观点与关于单元测试中什么是单元的讨论有关。伦敦学派认为类就是这样一个单元。来自于面向对象的编程背景，开发人员通常将类视为每个代码库的基础的原子构建块。这自然而然地导致了将类也视为测试中要验证的原子单元。这种倾向是可以理解的，但是会产生误导。

> TIP
> 
> Tests shouldn’t verify units of code. Rather, they should verify units of behavior: something that is meaningful for the problem domain and, ideally, something that a business person can recognize as useful. The number of classes it takes to implement such a unit of behavior is irrelevant. The unit could span across multiple classes or only one class, or even take up just a tiny method.
> 
> 测试不应该验证代码的单元。相反，他们应该验证行为单元：对问题领域有意义的东西，最好是业务人员能识别的有用的东西。实现这样一个行为单元所需的类的数量并不重要。这个单元可以跨越多个类，也可以只有一个类，甚至只占用一个小方法。

And so, aiming at better code granularity isn’t helpful. As long as the test checks a single unit of behavior, it’s a good test. Targeting something less than that can in fact damage your unit tests, as it becomes harder to understand exactly what these tests verify. A test should tell a story about the problem your code helps to solve, and this story should be cohesive and meaningful to a non-programmer.

因此，以更好的代码颗粒度为目标是没有用的。只要测试能检查一个单一的行为单元，它就是一个好的测试。瞄准比这更小的东西实际上会损害你的单元测试，因为它变得更难理解这些测试到底验证了什么。一个测试应该讲述一个关于你的代码帮助解决的问题的故事，这个故事应该是连贯的，对非程序员有意义的。

For instance, this is an example of a cohesive story:

例如，这是一个有凝聚力的故事的例子：

When I call my dog, he comes right to me.

当我叫我的狗的时候，它马上就来找我了。

Now compare it to the following:

现在把它与下面的故事进行比较：

When I call my dog, he moves his front left leg first, then the front right leg, his head turns, the tail start wagging…

当我叫我的狗时，它首先移动它的左前腿，然后是右前腿，它的头转向，尾巴开始摇动……

The second story makes much less sense. What’s the purpose of all those movements? Is the dog coming to me? Or is he running away? You can’t tell. This is what your tests start to look like when you target individual classes (the dog’s legs, head, and tail) instead of the actual behavior (the dog coming to his master). I talk more about this topic of observable behavior and how to differentiate it from internal implementation details in chapter 5.

第二个故事的意义就不大了。所有这些动作的目的是什么？这只狗是在向我走来吗？还是他在逃跑？你无法判断。这就是你的测试开始的样子，当你针对个别类别（狗的腿、头和尾巴）而不是实际行为（狗来到他的主人身边）。我在第 5 章中更多地讨论了可观察行为这个话题，以及如何将其与内部实现细节区分开来。

### [](#2-3-2-测试一个由相互连接的类组成的大图 "2.3.2 测试一个由相互连接的类组成的大图")2.3.2 测试一个由相互连接的类组成的大图

**Unit testing a large graph of interconnected classes**

The use of mocks in place of real collaborators can make it easier to test a class— especially when there’s a complicated dependency graph, where the class under test has dependencies, each of which relies on dependencies of its own, and so on, several layers deep. With test doubles, you can substitute the class’s immediate dependencies and thus break up the graph, which can significantly reduce the amount of preparation you have to do in a unit test. If you follow the classical school, you have to re-create the full object graph (with the exception of shared dependencies) just for the sake of setting up the system under test, which can be a lot of work.

使用 mocks 来代替真正的合作者可以使测试一个类变得更容易–特别是当有一个复杂的依赖图时，被测试的类有依赖，每个依赖都依赖于它自己的依赖，等等，有好几层深。通过测试替身，你可以替代类的直接依赖，从而打破图谱，这可以大大减少你在单元测试中的准备量。如果你遵循经典学派，你必须重新创建完整的对象图（共享的依赖除外），只是为了设置被测系统，这可能是一个很大的工作量。

Although this is all true, this line of reasoning focuses on the wrong problem. Instead of finding ways to test a large, complicated graph of interconnected classes, you should focus on not having such a graph of classes in the first place. More often than not, a large class graph is a result of a code design problem.

虽然这都是事实，但这种推理集中在错误的问题上。与其寻找方法来测试一个大型的、复杂的、相互关联的类图，不如把重点放在首先不要有这样一个类图上。更多时候，一个大的类图是代码设计问题的结果。

It’s actually a good thing that the tests point out this problem. As we discussed in chapter 1, the ability to unit test a piece of code is a good negative indicator—it predicts poor code quality with a relatively high precision. If you see that to unit test a class, you need to extend the test’s arrange phase beyond all reasonable limits, it’s a certain sign of trouble. The use of mocks only hides this problem; it doesn’t tackle the root cause. I talk about how to fix the underlying code design problem in part 2.

实际上，测试指出这个问题是件好事。正如我们在第 1 章中所讨论的，对一段代码进行单元测试的能力是一个很好的负面指标–它以相对较高的精度预测了糟糕的代码质量。如果你看到为了单元测试一个类，你需要把测试的准备阶段扩展到所有合理的范围之外，这肯定是一个麻烦的信号。使用 mocks 只是隐藏了这个问题，它并没有解决根本原因。我在第二部分中谈到了如何解决底层的代码设计问题。

### [](#2-3-3-揭示bug的精确位置 "2.3.3 揭示bug的精确位置")2.3.3 揭示bug的精确位置

**Revealing the precise bug location**

If you introduce a bug to a system with London-style tests, it normally causes only tests whose SUT contains the bug to fail. However, with the classical approach, tests that target the clients of the malfunctioning class can also fail. This leads to a ripple effect where a single bug can cause test failures across the whole system. As a result, it becomes harder to find the root of the issue. You might need to spend some time debugging the tests to figure it out.

如果你在一个有伦敦风格测试的系统中引入一个 bug，通常只导致其 SUT 包含该 bug 的测试失败。然而，在经典方法中，针对故障类的客户的测试也会失败。这就导致了一个连锁反应，一个错误可能会导致整个系统的测试失败。因此，要找到问题的根源变得更加困难。你可能需要花一些时间来调试测试以找出问题。

It’s a valid concern, but I don’t see it as a big problem. If you run your tests regularly (ideally, after each source code change), then you know what caused the bug— it’s what you edited last, so it’s not that difficult to find the issue. Also, you don’t have to look at all the failing tests. Fixing one automatically fixes all the others.

这是一个合理的担忧，但我不认为这是一个大问题。如果你定期运行你的测试（最好是在每次改变源代码后），那么你就知道是什么导致了这个错误–这是你最后编辑的内容，所以找到问题并不难。另外，你不需要看所有失败的测试。修复一个会自动修复其他所有的。

Furthermore, there’s some value in failures cascading all over the test suite. If a bug leads to a fault in not only one test but a whole lot of them, it shows that the piece of code you have just broken is of great value—the entire system depends on it. That’s useful information to keep in mind when working with the code.

此外，故障在测试套件中层层叠加也有一定的价值。如果一个错误不仅导致了一个测试的故障，而且导致了一大批测试的故障，这表明你刚刚破坏的那段代码是非常有价值的，整个系统都依赖于它。这是在处理代码时要记住的有用信息。

### [](#2-3-4-经典学派和伦敦学派的其他区别 "2.3.4 经典学派和伦敦学派的其他区别")2.3.4 经典学派和伦敦学派的其他区别

**Other differences between the classical and London schools**

Two remaining differences between the classical and London schools are

经典学派和伦敦学派之间剩下的两个区别是

*   Their approach to system design with test-driven development (TDD) 他们用测试驱动开发（TDD）进行系统设计的方法
*   The issue of over-specification 过度指定的问题

> **Test-driven development** 测试驱动开发
> 
> Test-driven development is a software development process that relies on tests to drive the project development. The process consists of three (some authors specify four) stages, which you repeat for every test case:
> 
> 测试驱动开发是一个依靠测试来驱动项目开发的软件开发过程。这个过程包括三个（有些作者规定为四个）阶段，你对每个测试用例都要重复这些阶段：
> 
> 1.  Write a failing test to indicate which functionality needs to be added and how it should behave. 写一个失败的测试，指出哪些功能需要添加，以及它应该如何表现。
> 2.  Write just enough code to make the test pass. At this stage, the code doesn’t have to be elegant or clean. 编写足够的代码，使测试通过。在这个阶段，代码不一定要优雅或干净。
> 3.  Refactor the code. Under the protection of the passing test, you can safely clean up the code to make it more readable and maintainable. 重构代码。在测试通过的保护下，你可以安全地清理代码，使其更可读和可维护。
> 
> Good sources on this topic are the two books I recommended earlier: Kent Beck’s Test-Driven Development: By Example, and Growing Object-Oriented Software, Guided by Tests by Steve Freeman and Nat Pryce.
> 
> 关于这个话题的好资料是我之前推荐的两本书： Kent Beck 的《Test-Driven Development: By Example》，以及 Steve Freeman 和 Nat Pryce 的《Growing Object-Oriented Software, Guided》。

The London style of unit testing leads to outside-in TDD, where you start from the higher-level tests that set expectations for the whole system. By using mocks, you specify which collaborators the system should communicate with to achieve the expected result. You then work your way through the graph of classes until you implement every one of them. Mocks make this design process possible because you can focus on one class at a time. You can cut off all of the SUT’s collaborators when testing it and thus postpone implementing those collaborators to a later time.

单元测试的伦敦风格导致了由外而内的 TDD，你从更高层次的测试开始，为整个系统设定预期。通过使用 mocks，你指定了系统应该与哪些合作者进行通信以达到预期的结果。然后，你通过类图来工作，直到你实现它们中的每一个。Mocks 使这个设计过程成为可能，因为你可以一次只关注一个类。你可以在测试时切断 SUT 的所有合作者，从而将实现这些合作者推迟到以后。

The classical school doesn’t provide quite the same guidance since you have to deal with the real objects in tests. Instead, you normally use the inside-out approach. In this style, you start from the domain model and then put additional layers on top of it until the software becomes usable by the end user.

经典学派并没有提供完全相同的指导，因为你必须在测试中处理真实的对象。相反，你通常使用由内向外的方法。在这种风格中，你从领域模型开始，然后在它上面添加附加层，直到软件可以被最终用户使用。

But the most crucial distinction between the schools is the issue of over-specification: that is, coupling the tests to the SUT’s implementation details. The London style tends to produce tests that couple to the implementation more often than the classical style. And this is the main objection against the ubiquitous use of mocks and the London style in general.

但是，这两个流派之间最关键的区别是过度指定的问题：也就是说，将测试与 SUT 的实现细节相联系。伦敦风格倾向于产生比经典风格更多的耦合到实现的测试。这也是反对普遍使用 mock 和伦敦风格的主要原因。

There’s much more to the topic of mocking. Starting with chapter 4, I gradually cover everything related to it.

关于 mocking 的话题还有很多。从第四章开始，我将逐步涵盖与之相关的所有内容。

## [](#2-4-两种学派的集成测试 "2.4 两种学派的集成测试")2.4 两种学派的集成测试

**Integration tests in the two schools**

The London and classical schools also diverge in their definition of an integration test. This disagreement flows naturally from the difference in their views on the isolation issue.

伦敦学派和经典学派在集成测试的定义上也有分歧。这种分歧自然来自于他们对隔离问题的不同看法。

The London school considers any test that uses a real collaborator object an integration test. Most of the tests written in the classical style would be deemed integration tests by the London school proponents. For an example, see listing 1.4, in which I first introduced the two tests covering the customer purchase functionality. That code is a typical unit test from the classical perspective, but it’s an integration test for a follower of the London school.

伦敦学派认为任何使用真实合作者对象的测试都是集成测试。大多数以经典风格编写的测试都被伦敦学派的支持者视为集成测试。对于一个例子，请看清单 1.4，在其中我首先介绍了两个涵盖客户购买功能的测试。从经典的角度看，这段代码是一个典型的单元测试，但对于伦敦学派的追随者来说，它是一个集成测试。

In this book, I use the classical definitions of both unit and integration testing. Again, a unit test is an automated test that has the following characteristics:

在这本书中，我使用了单元和集成测试的经典定义。同样，单元测试是一个具有以下特点的自动化测试：

*   It verifies a small piece of code, 它验证了一小段代码、
*   Does it quickly, 迅速完成、
*   And does it in an isolated manner. 并以一种隔离的方式进行。

Now that I’ve clarified what the first and third attributes mean, I’ll redefine them from the point of view of the classical school. A unit test is a test that

现在我已经澄清了第一和第三个属性的含义，我将从经典学派的角度重新定义它们。单元测试是一种测试，它

*   Verifies a single unit of behavior, 验证单一单元的行为、
*   Does it quickly, 快速完成、
*   And does it in isolation from other tests 并与其他测试隔离开来

An integration test, then, is a test that doesn’t meet one of these criteria. For example, a test that reaches out to a shared dependency—say, a database—can’t run in isolation from other tests. A change in the database’s state introduced by one test would alter the outcome of all other tests that rely on the same database if run in parallel. You’d have to take additional steps to avoid this interference. In particular, you would have to run such tests sequentially, so that each test would wait its turn to work with the shared dependency.

那么，集成测试就是不符合这些标准之一的测试。例如，一个接触到共享依赖关系的测试–比如，数据库–不能与其他测试隔离运行。一个测试引入的数据库状态的变化会改变所有其他依赖同一数据库的测试的结果，如果并行运行。你必须采取额外的措施来避免这种干扰。特别是，你必须按顺序运行这些测试，这样每个测试都会等待轮到它与共享的依赖工作。

Similarly, an outreach to an out-of-process dependency makes the test slow. A call to a database adds hundreds of milliseconds, potentially up to a second, of additional execution time. Milliseconds might not seem like a big deal at first, but when your test suite grows large enough, every second counts.

同样，对进程外依赖的外延会使测试变慢。对数据库的调用会增加数百毫秒的额外执行时间，有可能达到一秒钟。一开始，几毫秒可能不是什么大问题，但是当你的测试套件增长到足够大的时候，每一秒都很重要。

In theory, you could write a slow test that works with in-memory objects only, but it’s not that easy to do. Communication between objects inside the same memory space is much less expensive than between separate processes. Even if the test works with hundreds of in-memory objects, the communication with them will still execute faster than a call to a database.

从理论上讲，您可以编写一个仅适用于内存中对象的慢速测试，但这并不容易做到。同一内存空间内的对象之间的通信比独立进程之间的通信要便宜得多。即使测试与数百个内存中的对象一起工作，与它们的通信仍然会比调用数据库执行得快。

Finally, a test is an integration test when it verifies two or more units of behavior. This is often a result of trying to optimize the test suite’s execution speed. When you have two slow tests that follow similar steps but verify different units of behavior, it might make sense to merge them into one: one test checking two similar things runs faster than two more-granular tests. But then again, the two original tests would have been integration tests already (due to them being slow), so this characteristic usually isn’t decisive.

最后，当一个测试验证了两个或更多的行为单元时，它就是一个集成测试。这通常是试图优化测试套件的执行速度的结果。当你有两个缓慢的测试，遵循类似的步骤，但验证不同的行为单元，把它们合并成一个可能是有意义的：一个测试检查两个类似的东西，比两个更细的测试运行得更快。但话说回来，原来的两个测试已经是集成测试了（由于它们很慢），所以这个特点通常不是决定性的。

An integration test can also verify how two or more modules developed by separate teams work together. This also falls into the third bucket of tests that verify multiple units of behavior at once. But again, because such an integration normally requires an out-of-process dependency, the test will fail to meet all three criteria, not just one.

集成测试也可以验证由不同团队开发的两个或多个模块如何协同工作。这也属于第三类测试，即同时验证多个单元的行为。但同样的，因为这样的集成通常需要一个进程外的依赖，测试将无法满足所有三个标准，而不仅仅是一个。

Integration testing plays a significant part in contributing to software quality by verifying the system as a whole. I write about integration testing in detail in part 3.

集成测试通过验证整个系统，在促进软件质量方面发挥了重要作用。我在第三部分详细写了集成测试。

### [](#2-4-1-端到端测试是集成测试的一部分 "2.4.1 端到端测试是集成测试的一部分")2.4.1 端到端测试是集成测试的一部分

**End-to-end tests are a subset of integration tests**

In short, an integration test is a test that verifies that your code works in integration with shared dependencies, out-of-process dependencies, or code developed by other teams in the organization. There’s also a separate notion of an end-to-end test. End-to-end tests are a subset of integration tests. They, too, check to see how your code works with out-of-process dependencies. The difference between an end-to-end test and an integration test is that end-to-end tests usually include more of such dependencies.

简而言之，集成测试是验证你的代码与共享的依赖、进程外的依赖或组织中其他团队开发的代码集成工作的测试。还有一个单独的概念，就是端到端测试。端到端测试是集成测试的一个子集。他们也会检查你的代码如何与进程外的依赖一起工作。端到端测试和集成测试之间的区别是，端到端测试通常包括更多这样的依赖。

The line is blurred at times, but in general, an integration test works with only one or two out-of-process dependencies. On the other hand, an end-to-end test works with all out-of-process dependencies, or with the vast majority of them. Hence the name end-to-end, which means the test verifies the system from the end user’s point of view, including all the external applications this system integrates with (see figure 2.6).

这条线有时是模糊的，但一般来说，集成测试只与一个或两个进程外的依赖一起工作。另一方面，端到端测试适用于所有进程外的依赖，或绝大多数的依赖。因此被称为端到端，这意味着测试从最终用户的角度验证系统，包括这个系统与之集成的所有外部应用程序（见图2.6）。

![image-20230409202805750](~/assets/images/unit-testing-2/image-20230409202805750.png)

Figure 2.6 End-to-end tests normally include all or almost all out-of-process dependencies in the scope. Integration tests check only one or two such dependencies—those that are easier to set up automatically, such as the database or the file system.

图 2.6 端到端测试通常包括所有或几乎所有进程外的依赖的范围。集成测试只检查一两个这样的依赖–那些更容易自动设置的，如数据库或文件系统。

People also use such terms as UI tests (UI stands for user interface), GUI tests (GUI is graphical user interface), and functional tests. The terminology is ill-defined, but in general, these terms are all synonyms.

人们还使用诸如 UI 测试（UI 代表用户界面）、GUI 测试（GUI 是图形用户界面）和功能测试等术语。术语定义不清，但一般来说，这些术语都是同义词。

Let’s say your application works with three out-of-process dependencies: a database, the file system, and a payment gateway. A typical integration test would include only the database and file system in scope and use a test double to replace the payment gateway. That’s because you have full control over the database and file system, and thus can easily bring them to the required state in tests, whereas you don’t have the same degree of control over the payment gateway. With the payment gateway, you may need to contact the payment processor organization to set up a special test account. You might also need to check that account from time to time to manually clean up all the payment charges left over from the past test executions.

假设你的应用程序与三个进程外的依赖一起工作：一个数据库，文件系统和一个支付网关。一个典型的集成测试将只包括数据库和文件系统的范围，并使用一个测试替身来代替支付网关。这是因为你可以完全控制数据库和文件系统，因此可以很容易地在测试中使它们达到所需的状态，而你对支付网关没有同样程度的控制。对于支付网关，你可能需要联系支付处理机构来设置一个特殊的测试账户。你可能还需要不时地检查该账户，手动清理过去测试执行中留下的所有支付费用。

Since end-to-end tests are the most expensive in terms of maintenance, it’s better to run them late in the build process, after all the unit and integration tests have passed. You may possibly even run them only on the build server, not on individual developers’ machines.

由于端到端测试在维护方面是最昂贵的，所以最好是在构建过程的后期，在所有的单元和集成测试都通过后再运行它们。你甚至可以只在构建服务器上运行它们，而不是在单个开发人员的机器上。

Keep in mind that even with end-to-end tests, you might not be able to tackle all of the out-of-process dependencies. There may be no test version of some dependencies, or it may be impossible to bring those dependencies to the required state automatically. So you may still need to use a test double, reinforcing the fact that there isn’t a distinct line between integration and end-to-end tests.

请记住，即使有端到端的测试，你也可能无法解决所有进程外的依赖。某些依赖项可能没有测试版本，或者可能无法自动将这些依赖项置于所需状态。因此，你可能仍然需要使用测试替身，这加强了一个事实，即集成测试和端到端测试之间并没有明显的界限。

## [](#2-5-总结 "2.5 总结")2.5 总结

**Summary**

*   Throughout this chapter, I’ve refined the definition of a unit test: 在这一章中，我已经完善了单元测试的定义：
    *   A unit test verifies a single unit of behavior, 一个单元测试验证一个单一的行为单元、
    *   Does it quickly, 迅速完成、
    *   And does it in isolation from other tests. 并与其他测试隔离开来。
*   The isolation issue is disputed the most. The dispute led to the formation of two schools of unit testing: the classical (Detroit) school, and the London (mockist) school. This difference of opinion affects the view of what constitutes a unit and the treatment of the system under test’s (SUT’s) dependencies. 隔离的问题是最有争议的。这个争议导致了两个单元测试流派的形成：经典（底特律）学派和伦敦（mockist）学派。这种意见分歧影响了对什么是单元的看法以及对被测系统（SUT）依赖的处理。
    *   – The London school states that the units under test should be isolated from each other. A unit under test is a unit of code, usually a class. All of its dependencies, except immutable dependencies, should be replaced with test doubles in tests. 伦敦学派指出，被测单元应该是相互隔离的。一个被测单元是一个代码单元，通常是一个类。它的所有依赖关系，除了不可变的依赖关系，应该在测试中用测试替身来代替。
    *   – The classical school states that the unit tests need to be isolated from each other, not units. Also, a unit under test is a unit of behavior, not a unit of code. Thus, only shared dependencies should be replaced with test doubles. Shared dependencies are dependencies that provide means for tests to affect each other’s execution flow. 经典学派指出，单元测试需要相互隔离，而不是单元。另外，被测试的单元是行为的单元，而不是代码的单元。因此，只有共享的依赖才应该被替换成测试替身。共享的依赖是指为测试提供影响彼此执行流程的手段的依赖。
*   The London school provides the benefits of better granularity, the ease of testing large graphs of interconnected classes, and the ease of finding which functionality contains a bug after a test failure. 伦敦学派提供了更好的颗粒度的好处，易于测试相互连接的类的大图，以及易于在测试失败后发现哪个功能包含一个错误。
*   The benefits of the London school look appealing at first. However, they introduce several issues. First, the focus on classes under test is misplaced: tests should verify units of behavior, not units of code. Furthermore, the inability to unit test a piece of code is a strong sign of a problem with the code design. The use of test doubles doesn’t fix this problem, but rather only hides it. And finally, while the ease of determining which functionality contains a bug after a test failure is helpful, it’s not that big a deal because you often know what caused the bug anyway—it’s what you edited last. 伦敦学派的好处一开始看起来很吸引人。然而，它们引入了几个问题。首先，对被测类的关注点是错误的：测试应该验证行为单元，而不是代码单元。此外，无法对一段代码进行单元测试是代码设计有问题的一个强烈信号。使用测试替身并不能解决这个问题，而只是把它隐藏起来。最后，虽然在测试失败后很容易确定哪个功能含有错误是有帮助的，但这并不是什么大问题，因为无论如何你都知道是什么导致了这个错误–它是你最后编辑的内容。
*   The biggest issue with the London school of unit testing is the problem of overspecification—coupling tests to the SUT’s implementation details. 伦敦学派的单元测试最大的问题是过度指定的问题–将测试与 SUT 的实现细节相联系。
*   An integration test is a test that doesn’t meet at least one of the criteria for a unit test. End-to-end tests are a subset of integration tests; they verify the system from the end user’s point of view. End-to-end tests reach out directly to all or almost all out-of-process dependencies your application works with. 集成测试是一个不符合单元测试的至少一个标准的测试。端到端测试是集成测试的一个子集；它们从终端用户的角度验证系统。端到端测试直接访问到所有或几乎所有进程外的你的应用程序与之合作的依赖。
*   For a canonical book about the classical style, I recommend Kent Beck’s TestDriven Development: By Example. For more on the London style, see Growing ObjectOriented Software, Guided by Tests, by Steve Freeman and Nat Pryce. For further reading about working with dependencies, I recommend Dependency Injection: Principles, Practices, Patterns by Steven van Deursen and Mark Seemann. 关于经典风格的典型书籍，我推荐Kent Beck的《TestDriven Development: By Example》。关于伦敦风格的更多信息，请参阅 Steve Freeman 和 Nat Pryce 的《Growing ObjectOriented Software, Guided by Tests》。关于依赖的进一步阅读，我推荐 Steven van Deursen 和 Mark Seemann 的《Dependency Injection: Principles, Practices, Patterns》。