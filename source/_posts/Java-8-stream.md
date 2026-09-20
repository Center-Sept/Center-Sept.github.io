---
title: "Java 8 stream"
date: 2023-03-24 00:00:00
tags:
  - "java8"
categories: []
---
## Java 8 stream

### 流的创建

1.使用Collection下的 stream() 和 parallelStream() 方法

```java
List<String> list = new ArrayList<>();
Stream<String> stream = list.stream(); //获取一个顺序流
Stream<String> parallelStream = list.parallelStream(); //获取一个并行流
```

2 使用Arrays 中的 stream() 方法，将数组转成流

```java
Integer[] nums = new Integer[10];
Stream<Integer> stream = Arrays.stream(nums);
```

3.使用Stream中的静态方法：of()、iterate()、generate()

```java
Stream<Integer> stream = Stream.of(1,2,3,4,5,6);

Stream<Integer> stream2 = Stream.iterate(0, (x) -> x + 2).limit(6);
stream2.forEach(System.out::println); // 0 2 4 6 8 10

Stream<Double> stream3 = Stream.generate(Math::random).limit(2);
stream3.forEach(System.out::println);
```

4.使用 BufferedReader.lines() 方法，将每行内容转成流

```java
BufferedReader reader = new BufferedReader(new FileReader("F:\\test_stream.txt"));
Stream<String> lineStream = reader.lines();
lineStream.forEach(System.out::println);
```

5.使用 Pattern.splitAsStream() 方法，将字符串分隔成流

```java
Pattern pattern = Pattern.compile(",");
Stream<String> stringStream = pattern.splitAsStream("a,b,c,d");
stringStream.forEach(System.out::println);
```

流的中间操作

1.筛选与切片

filter：过滤流中的某些元素  
limit(n)：获取n个元素  
skip(n)：跳过n元素，配合limit(n)可实现分页  
distinct：通过流中元素的 hashCode() 和 equals() 去除重复元素

```java
Stream<Integer> stream = Stream.of(6, 4, 6, 7, 3, 9, 8, 10, 12, 14, 14);
 
Stream<Integer> newStream = stream.filter(s -> s > 5) //6 6 7 9 8 10 12 14 14
        .distinct() //6 7 9 8 10 12 14
        .skip(2) //9 8 10 12 14
        .limit(2); //9 8
newStream.forEach(System.out::println);
```

2.映射

map：接收一个函数作为参数，该函数会被应用到每个元素上，并将其映射成一个新的元素。  
flatMap：接收一个函数作为参数，将流中的每个值都换成另一个流，然后把所有流连接成一个流。

```java
List<String> list = Arrays.asList("a,b,c", "1,2,3");
 
//将每个元素转成一个新的且不带逗号的元素
Stream<String> s1 = list.stream().map(s -> s.replaceAll(",", ""));
s1.forEach(System.out::println); // abc  123
 
Stream<String> s3 = list.stream().flatMap(s -> {
    //将每个元素转换成一个stream
    String[] split = s.split(",");
    Stream<String> s2 = Arrays.stream(split);
    return s2;
});
s3.forEach(System.out::println); // a b c 1 2 3
```

## list转map方法

背景  
在最近的工作开发之中，慢慢习惯了很多Java8中的Stream的用法，很方便而且也可以并行的去执行这个流，这边去写一下昨天遇到的一个list转map的场景。  
list转map在Java8中stream的应用  
常用方式  
1.利用Collectors.toMap方法进行转换

```java
public Map<Long, String> getIdNameMap(List<Account> accounts) {
	return accounts.stream().collect(Collectors.toMap(Account::getId, Account::getUsername));
}
```

其中第一个参数就是可以，第二个参数就是value的值。

2.收集对象实体本身  
- 在开发过程中我们也需要有时候对自己的list中的实体按照其中的一个字段进行分组（比如 id -\>List），这时候要设置map的value值是实体本身。

```java
public Map<Long, Account> getIdAccountMap(List<Account> accounts) {
	return accounts.stream().collect(Collectors.toMap(Account::getId, item -> item));
}
```

account -\> account是一个返回本身的lambda表达式，其实还可以使用Function接口中的一个默认方法 Function.identity()，这个方法返回自身对象，更加简洁

重复key的情况。  
在list转为map时，作为key的值有可能重复，这时候流的处理会抛出个异常：Java.lang.IllegalStateException:Duplicate key。这时候就要在toMap方法中指定当key冲突时key的选择。(这里是选择第二个key覆盖第一个key)

```java
public Map<String, Account> getNameAccountMap(List<Account> accounts) {
	return accounts.stream().collect(Collectors.toMap(Account::getUsername, Function.identity(), (key1, key2) -> key2));
}
```

用groupingBy 或者 partitioningBy进行分组  
根据一个字段或者属性分组也可以直接用groupingBy方法，很方便。

```java
Map<Integer, List<Person>> personGroups = Stream.generate(new PersonSupplier()).
	limit(100).
	collect(Collectors.groupingBy(Person::getAge));
	Iterator it = personGroups.entrySet().iterator();
	while (it.hasNext()) {
		Map.Entry<Integer, List<Person>> persons = (Map.Entry) it.next();
		System.out.println("Age " + persons.getKey() + " = " + persons.getValue().size());
	}
```

partitioningBy可以理解为特殊的groupingBy，key值为true和false，当然此时方法中的参数为一个判断语句（用于判断的函数式接口）

```java
Map<Boolean, List<Person>> children = Stream.generate(new PersonSupplier()).
limit(100).
collect(Collectors.partitioningBy(p -> p.getAge() < 18));
System.out.println("Children number: " + children.get(true).size());
System.out.println("Adult number: " + children.get(false).size());
```
