"""
Curated DSA Problems Data
Inspired by LeetCode and CodeChef problems
"""

from datetime import date
from typing import List, Dict, Any
from enum import Enum


class DSADifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


# Topic categories
TOPICS = [
    "Arrays",
    "Strings", 
    "Algorithms",
    "Dynamic Programming",
    "Recursion",
    "Linked List",
    "Trees",
    "Graphs",
    "Hash Tables",
    "Greedy",
    "Two Pointers",
    "Sliding Window",
    "Stack",
    "Queue"
]


# Curated problems data
CURATED_PROBLEMS: List[Dict[str, Any]] = [
    # ==================== EASY PROBLEMS ====================
    {
        "id": "two-sum",
        "title": "Two Sum",
        "slug": "two-sum",
        "difficulty": DSADifficulty.EASY,
        "category": "Arrays",
        "tags": ["Arrays", "Hash Tables"],
        "description": """Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

You can return the answer in any order.""",
        "constraints": [
            "2 <= nums.length <= 10^4",
            "-10^9 <= nums[i] <= 10^9",
            "-10^9 <= target <= 10^9",
            "Only one valid answer exists."
        ],
        "inputFormat": "First line contains n (number of elements). Second line contains n integers. Third line contains target sum.",
        "outputFormat": "Print the indices of the two numbers that add up to target.",
        "exampleInput": "nums = [2,7,11,15], target = 9",
        "exampleOutput": "[0,1]",
        "explanation": "Because nums[0] + nums[1] == 9, we return [0, 1].",
        "platformLink": "https://leetcode.com/problems/two-sum/",
        "companies_asked": ["Google", "Amazon", "Apple", "Microsoft", "Facebook"],
        "frequency_score": 0.95
    },
    {
        "id": "reverse-string",
        "title": "Reverse String",
        "slug": "reverse-string",
        "difficulty": DSADifficulty.EASY,
        "category": "Strings",
        "tags": ["Strings", "Two Pointers"],
        "description": """Write a function that reverses a string. The input string is given as an array of characters s.

You must do this by modifying the input array in-place with O(1) extra memory.""",
        "constraints": [
            "1 <= s.length <= 10^5",
            "s[i] is a printable ascii character."
        ],
        "inputFormat": "A string s containing printable ASCII characters.",
        "outputFormat": "The reversed string.",
        "exampleInput": 's = ["h","e","l","l","o"]',
        "exampleOutput": '["o","l","l","e","h"]',
        "explanation": "The string is reversed in place.",
        "platformLink": "https://leetcode.com/problems/reverse-string/",
        "companies_asked": ["Amazon", "Microsoft", "Apple"],
        "frequency_score": 0.85
    },
    {
        "id": "valid-parentheses",
        "title": "Valid Parentheses",
        "slug": "valid-parentheses",
        "difficulty": DSADifficulty.EASY,
        "category": "Stack",
        "tags": ["Stack", "Strings"],
        "description": """Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.

An input string is valid if:
1. Open brackets must be closed by the same type of brackets.
2. Open brackets must be closed in the correct order.
3. Every close bracket has a corresponding open bracket of the same type.""",
        "constraints": [
            "1 <= s.length <= 10^4",
            "s consists of parentheses only '()[]{}'."
        ],
        "inputFormat": "A string s containing parentheses characters.",
        "outputFormat": "Return true if valid, false otherwise.",
        "exampleInput": "s = \"()\"",
        "exampleOutput": "true",
        "explanation": "The parentheses are properly balanced.",
        "platformLink": "https://leetcode.com/problems/valid-parentheses/",
        "companies_asked": ["Amazon", "Google", "Facebook", "Microsoft"],
        "frequency_score": 0.90
    },
    {
        "id": "merge-sorted-arrays",
        "title": "Merge Sorted Array",
        "slug": "merge-sorted-arrays",
        "difficulty": DSADifficulty.EASY,
        "category": "Arrays",
        "tags": ["Arrays", "Two Pointers", "Sorting"],
        "description": """You are given two integer arrays nums1 and nums2, sorted in non-decreasing order, and two integers m and n, representing the number of elements in nums1 and nums2 respectively.

Merge nums1 and nums2 into a single array sorted in non-decreasing order.

The final sorted array should be stored inside nums1. nums1 has a length of m + n, where the first m elements denote the elements that should be merged, and the last n elements are set to 0 and should be ignored. nums2 has a length of n.""",
        "constraints": [
            "nums1.length == m",
            "nums2.length == n",
            "0 <= m, n <= 200",
            "-10^9 <= nums1[i], nums2[j] <= 10^9"
        ],
        "inputFormat": "Two sorted arrays nums1 and nums2 with their sizes m and n.",
        "outputFormat": "Merged sorted array in nums1.",
        "exampleInput": "nums1 = [1,2,3,0,0,0], m = 3, nums2 = [2,5,6], n = 3",
        "exampleOutput": "[1,2,2,3,5,6]",
        "explanation": "The arrays are merged to form the sorted array.",
        "platformLink": "https://leetcode.com/problems/merge-sorted-array/",
        "companies_asked": ["Amazon", "Microsoft", "Google"],
        "frequency_score": 0.75
    },
    {
        "id": "best-time-to-buy-and-sell-stock",
        "title": "Best Time to Buy and Sell Stock",
        "slug": "best-time-to-buy-and-sell-stock",
        "difficulty": DSADifficulty.EASY,
        "category": "Algorithms",
        "tags": ["Arrays", "Dynamic Programming"],
        "description": """You are given an array prices where prices[i] is the price of a given stock on the ith day.

You want to maximize your profit by choosing a single day to buy one stock and choosing a different day in the future to sell that stock.

Return the maximum profit you can achieve from this transaction. If you cannot achieve any profit, return 0.""",
        "constraints": [
            "1 <= prices.length <= 10^5",
            "0 <= prices[i] <= 10^4"
        ],
        "inputFormat": "An array of stock prices.",
        "outputFormat": "Maximum profit possible.",
        "exampleInput": "prices = [7,1,5,3,6,4]",
        "exampleOutput": "5",
        "explanation": "Buy on day 2 (price = 1) and sell on day 5 (price = 6), profit = 6-1 = 5.",
        "platformLink": "https://leetcode.com/problems/best-time-to-buy-and-sell-stock/",
        "companies_asked": ["Amazon", "Facebook", "Microsoft", "Apple"],
        "frequency_score": 0.88
    },
    {
        "id": "linked-list-cycle",
        "title": "Linked List Cycle",
        "slug": "linked-list-cycle",
        "difficulty": DSADifficulty.EASY,
        "category": "Linked List",
        "tags": ["Linked List", "Hash Tables", "Two Pointers"],
        "description": """Given head, the head of a linked list, determine if the linked list has a cycle in it.

There is a cycle in a linked list if there is some node in the list that can be reached again by continuously following the next pointer. Internally, pos is used to denote the index of the node that tail's next pointer is connected to. Note that pos is not passed as a parameter.

Return true if there is a cycle in the linked list. Otherwise, return false.""",
        "constraints": [
            "The number of nodes in the list is in the range [0, 10^4]",
            "-10^5 <= Node.val <= 10^5",
            "pos is -1 or a valid index in the linked-list."
        ],
        "inputFormat": "Head of a linked list.",
        "outputFormat": "True if cycle exists, False otherwise.",
        "exampleInput": "head = [3,2,0,-4], pos = 1",
        "exampleOutput": "true",
        "explanation": "There is a cycle where tail connects to index 1.",
        "platformLink": "https://leetcode.com/problems/linked-list-cycle/",
        "companies_asked": ["Amazon", "Google", "Microsoft", "Apple"],
        "frequency_score": 0.82
    },
    {
        "id": "maximum-subarray",
        "title": "Maximum Subarray",
        "slug": "maximum-subarray",
        "difficulty": DSADifficulty.EASY,
        "category": "Algorithms",
        "tags": ["Arrays", "Dynamic Programming", "Divide and Conquer"],
        "description": """Given an integer array nums, find the subarray with the largest sum, and return its sum.""",
        "constraints": [
            "1 <= nums.length <= 10^5",
            "-10^4 <= nums[i] <= 10^4"
        ],
        "inputFormat": "An array of integers.",
        "outputFormat": "Maximum sum of any non-empty subarray.",
        "exampleInput": "nums = [-2,1,-3,4,-1,2,1,-5,4]",
        "exampleOutput": "6",
        "explanation": "The subarray [4,-1,2,1] has the largest sum 6.",
        "platformLink": "https://leetcode.com/problems/maximum-subarray/",
        "companies_asked": ["Amazon", "Microsoft", "Apple", "LinkedIn"],
        "frequency_score": 0.92
    },
    {
        "id": "valid-palindrome",
        "title": "Valid Palindrome",
        "slug": "valid-palindrome",
        "difficulty": DSADifficulty.EASY,
        "category": "Strings",
        "tags": ["Strings", "Two Pointers"],
        "description": """A phrase is a palindrome if, after converting all uppercase letters into lowercase letters and removing all non-alphanumeric characters, it reads the same forward and backward. Alphanumeric characters include letters and numbers.

Given a string s, return true if it is a palindrome, or false otherwise.""",
        "constraints": [
            "1 <= s.length <= 2 * 10^5",
            "s consists only of printable ASCII characters."
        ],
        "inputFormat": "A string s.",
        "outputFormat": "True if palindrome, False otherwise.",
        "exampleInput": 's = "A man, a plan, a canal: Panama"',
        "exampleOutput": "true",
        "explanation": "\"amanaplanacanalpanama\" is a palindrome.",
        "platformLink": "https://leetcode.com/problems/valid-palindrome/",
        "companies_asked": ["Facebook", "Microsoft", "Amazon"],
        "frequency_score": 0.78
    },

    # ==================== MEDIUM PROBLEMS ====================
    {
        "id": "longest-substring-without-repeating",
        "title": "Longest Substring Without Repeating Characters",
        "slug": "longest-substring-without-repeating",
        "difficulty": DSADifficulty.MEDIUM,
        "category": "Strings",
        "tags": ["Hash Tables", "Strings", "Sliding Window"],
        "description": """Given a string s, find the length of the longest substring without repeating characters.""",
        "constraints": [
            "0 <= s.length <= 5 * 10^4",
            "s consists of English letters, digits, symbols and spaces."
        ],
        "inputFormat": "A string s.",
        "outputFormat": "Length of longest substring without repeating characters.",
        "exampleInput": 's = "abcabcbb"',
        "exampleOutput": "3",
        "explanation": "The answer is \"abc\", with the length of 3.",
        "platformLink": "https://leetcode.com/problems/longest-substring-without-repeating-characters/",
        "companies_asked": ["Amazon", "Google", "Facebook", "Microsoft", "Apple"],
        "frequency_score": 0.95
    },
    {
        "id": "container-with-most-water",
        "title": "Container With Most Water",
        "slug": "container-with-most-water",
        "difficulty": DSADifficulty.MEDIUM,
        "category": "Algorithms",
        "tags": ["Arrays", "Two Pointers", "Greedy"],
        "description": """You are given an integer array height of length n. There are n vertical lines drawn such that the two endpoints of the ith line are (i, 0) and (i, height[i]).

Find two lines that together with the x-axis form a container, such that the container contains the most water.

Return the maximum amount of water a container can store.""",
        "constraints": [
            "n == height.length",
            "2 <= n <= 10^5",
            "0 <= height[i] <= 10^4"
        ],
        "inputFormat": "Array of integers representing heights.",
        "outputFormat": "Maximum water container can hold.",
        "exampleInput": "height = [1,8,6,2,5,4,8,3,7]",
        "exampleOutput": "49",
        "explanation": "The max area is obtained by lines at index 1 and 8.",
        "platformLink": "https://leetcode.com/problems/container-with-most-water/",
        "companies_asked": ["Amazon", "Google", "Microsoft", "Facebook"],
        "frequency_score": 0.88
    },
    {
        "id": "3sum",
        "title": "3Sum",
        "slug": "3sum",
        "difficulty": DSADifficulty.MEDIUM,
        "category": "Arrays",
        "tags": ["Arrays", "Two Pointers", "Sorting"],
        "description": """Given an integer array nums, return all the triplets [nums[i], nums[j], nums[k]] such that i != j, i != k, and j != k, and nums[i] + nums[j] + nums[k] == 0.

Notice that the solution set must not contain duplicate triplets.""",
        "constraints": [
            "0 <= nums.length <= 3000",
            "-10^5 <= nums[i] <= 10^5"
        ],
        "inputFormat": "An array of integers nums.",
        "outputFormat": "List of all unique triplets that sum to zero.",
        "exampleInput": "nums = [-1,0,1,2,-1,-4]",
        "exampleOutput": "[[-1,-1,2],[-1,0,1]]",
        "explanation": "The distinct triplets are those summing to zero.",
        "platformLink": "https://leetcode.com/problems/3sum/",
        "companies_asked": ["Amazon", "Facebook", "Google", "Microsoft", "Apple"],
        "frequency_score": 0.92
    },
    {
        "id": "coin-change",
        "title": "Coin Change",
        "slug": "coin-change",
        "difficulty": DSADifficulty.MEDIUM,
        "category": "Dynamic Programming",
        "tags": ["Dynamic Programming", "Arrays"],
        "description": """You are given an integer array coins representing coins of different denominations and an integer amount representing a total amount of money.

Return the fewest number of coins that you need to make up that amount. If that amount of money cannot be made up by any combination of the coins, return -1.

You may assume that you have an infinite number of each kind of coin.""",
        "constraints": [
            "1 <= coins.length <= 12",
            "1 <= coins[i] <= 2^31 - 1",
            "0 <= amount <= 10^4"
        ],
        "inputFormat": "Array of coin denominations and target amount.",
        "outputFormat": "Minimum number of coins needed.",
        "exampleInput": "coins = [1,2,5], amount = 11",
        "exampleOutput": "3",
        "explanation": "11 = 5 + 5 + 1",
        "platformLink": "https://leetcode.com/problems/coin-change/",
        "companies_asked": ["Amazon", "Google", "Apple", "Facebook"],
        "frequency_score": 0.90
    },
    {
        "id": "number-of-islands",
        "title": "Number of Islands",
        "slug": "number-of-islands",
        "difficulty": DSADifficulty.MEDIUM,
        "category": "Graphs",
        "tags": ["Graphs", "Depth-First Search", "Breadth-First Search", "Union Find"],
        "description": """Given an m x n 2D binary grid which represents a map of '1's (land) and '0's (water), return the number of islands.

An island is surrounded by water and is formed by connecting adjacent lands horizontally or vertically. You may assume all four edges of the grid are all surrounded by water.""",
        "constraints": [
            "m == grid.length",
            "n == grid[i].length",
            "1 <= m, n <= 300",
            "grid[i][j] is '0' or '1'."
        ],
        "inputFormat": "2D grid of '1's and '0's.",
        "outputFormat": "Number of islands.",
        "exampleInput": "grid = [\n  [\"1\",\"1\",\"1\",\"1\",\"0\"],\n  [\"1\",\"1\",\"0\",\"1\",\"0\"],\n  [\"1\",\"1\",\"0\",\"0\",\"0\"],\n  [\"0\",\"0\",\"0\",\"0\",\"0\"]\n]",
        "exampleOutput": "1",
        "explanation": "There is one island in the grid.",
        "platformLink": "https://leetcode.com/problems/number-of-islands/",
        "companies_asked": ["Amazon", "Facebook", "Microsoft", "Google", "Apple"],
        "frequency_score": 0.87
    },
    {
        "id": "binary-tree-inorder-traversal",
        "title": "Binary Tree Inorder Traversal",
        "slug": "binary-tree-inorder-traversal",
        "difficulty": DSADifficulty.MEDIUM,
        "category": "Trees",
        "tags": ["Trees", "Recursion", "Stack"],
        "description": """Given the root of a binary tree, return the inorder traversal of its nodes' values.""",
        "constraints": [
            "The number of nodes in the tree is in the range [0, 100].",
            "-100 <= Node.val <= 100"
        ],
        "inputFormat": "Root of a binary tree.",
        "outputFormat": "Inorder traversal of node values.",
        "exampleInput": "root = [1,null,2,3]",
        "exampleOutput": "[1,3,2]",
        "explanation": "Inorder traversal visits left, root, right.",
        "platformLink": "https://leetcode.com/problems/binary-tree-inorder-traversal/",
        "companies_asked": ["Microsoft", "Amazon", "Facebook"],
        "frequency_score": 0.75
    },
    {
        "id": "validate-binary-search-tree",
        "title": "Validate Binary Search Tree",
        "slug": "validate-binary-search-tree",
        "difficulty": DSADifficulty.MEDIUM,
        "category": "Trees",
        "tags": ["Trees", "Depth-First Search", "Binary Search Tree"],
        "description": """Given the root of a binary tree, determine if it is a valid binary search tree (BST).

A valid BST is defined as follows:
- The left subtree of a node contains only nodes with keys less than the node's key.
- The right subtree of a node contains only nodes with keys greater than the node's key.
- Both the left and right subtrees must also be binary search trees.""",
        "constraints": [
            "The number of nodes in the tree is in the range [1, 10^4].",
            "-2^31 <= Node.val <= 2^31 - 1"
        ],
        "inputFormat": "Root of a binary tree.",
        "outputFormat": "True if valid BST, False otherwise.",
        "exampleInput": "root = [2,1,3]",
        "exampleOutput": "true",
        "explanation": "Left subtree values < root, right subtree values > root.",
        "platformLink": "https://leetcode.com/problems/validate-binary-search-tree/",
        "companies_asked": ["Amazon", "Facebook", "Microsoft", "Bloomberg"],
        "frequency_score": 0.85
    },
    {
        "id": "lru-cache",
        "title": "LRU Cache",
        "slug": "lru-cache",
        "difficulty": DSADifficulty.MEDIUM,
        "category": "Algorithms",
        "tags": ["Hash Tables", "Linked List", "Design", "Queue"],
        "description": """Design a data structure that follows the constraints of a Least Recently Used (LRU) cache.

Implement the LRUCache class:
- LRUCache(int capacity) Initialize the LRU cache with positive size capacity.
- int get(int key) Return the value of the key if it exists, otherwise return -1.
- void put(int key, int value) Update the value of the key if it exists. Otherwise, add the key-value pair to the cache. If the number of keys exceeds the capacity, evict the least recently used key.""",
        "constraints": [
            "1 <= capacity <= 3000",
            "0 <= key <= 10^4",
            "0 <= value <= 10^5",
            "At most 2 * 10^5 calls will be made to get and put."
        ],
        "inputFormat": "Operations on LRU cache.",
        "outputFormat": "Values for get operations.",
        "exampleInput": '["LRUCache", "put", "put", "get", "put", "get", "put", "get", "get", "get"]\n[[2], [1, 1], [2, 2], [1], [3, 3], [2], [4, 4], [1], [3], [4]]',
        "exampleOutput": "[null, null, null, 1, null, -1, null, -1, 3, 4]",
        "explanation": "LRU cache operations with capacity 2.",
        "platformLink": "https://leetcode.com/problems/lru-cache/",
        "companies_asked": ["Amazon", "Google", "Microsoft", "Facebook", "Apple"],
        "frequency_score": 0.88
    },
    {
        "id": "sort-colors",
        "title": "Sort Colors",
        "slug": "sort-colors",
        "difficulty": DSADifficulty.MEDIUM,
        "category": "Algorithms",
        "tags": ["Arrays", "Two Pointers", "Sorting", "Dutch National Flag"],
        "description": """Given an array nums with n objects colored red, white, or blue, sort them in-place so that objects of the same color are adjacent, with the colors in the order red, white, and blue.

We will use the integers 0, 1, and 2 to represent the color red, white, and blue, respectively.

You must solve this problem without using the library's sort function.""",
        "constraints": [
            "n == nums.length",
            "1 <= n <= 300",
            "nums[i] is either 0, 1, or 2."
        ],
        "inputFormat": "Array of 0s, 1s, and 2s.",
        "outputFormat": "Sorted array in-place.",
        "exampleInput": "nums = [2,0,2,1,1,0]",
        "exampleOutput": "[0,0,1,1,2,2]",
        "explanation": "Array sorted in the order 0s, 1s, 2s.",
        "platformLink": "https://leetcode.com/problems/sort-colors/",
        "companies_asked": ["Amazon", "Microsoft", "Facebook", "Adobe"],
        "frequency_score": 0.80
    },

    # ==================== HARD PROBLEMS ====================
    {
        "id": "median-of-two-sorted-arrays",
        "title": "Median of Two Sorted Arrays",
        "slug": "median-of-two-sorted-arrays",
        "difficulty": DSADifficulty.HARD,
        "category": "Algorithms",
        "tags": ["Arrays", "Binary Search", "Divide and Conquer"],
        "description": """Given two sorted arrays nums1 and nums2 of size m and n respectively, return the median of the two sorted arrays.

The overall run time complexity should be O(log (m+n)).""",
        "constraints": [
            "nums1.length == m",
            "nums2.length == n",
            "0 <= m <= 1000",
            "0 <= n <= 1000",
            "1 <= m + n <= 2000",
            "-10^6 <= nums1[i], nums2[i] <= 10^6"
        ],
        "inputFormat": "Two sorted arrays.",
        "outputFormat": "Median of combined arrays.",
        "exampleInput": "nums1 = [1,3], nums2 = [2]",
        "exampleOutput": "2.00000",
        "explanation": "Merged array = [1,2,3], median = 2.",
        "platformLink": "https://leetcode.com/problems/median-of-two-sorted-arrays/",
        "companies_asked": ["Amazon", "Google", "Microsoft", "Apple", "Facebook"],
        "frequency_score": 0.95
    },
    {
        "id": "trapping-rain-water",
        "title": "Trapping Rain Water",
        "slug": "trapping-rain-water",
        "difficulty": DSADifficulty.HARD,
        "category": "Algorithms",
        "tags": ["Arrays", "Two Pointers", "Dynamic Programming", "Stack", "Monotonic Stack"],
        "description": """Given n non-negative integers representing an elevation map where the width of each bar is 1, compute how much water it can trap after raining.""",
        "constraints": [
            "n == height.length",
            "1 <= n <= 2 * 10^4",
            "0 <= height[i] <= 10^5"
        ],
        "inputFormat": "Array of non-negative integers representing elevation.",
        "outputFormat": "Total water trapped.",
        "exampleInput": "height = [0,1,0,2,1,0,1,3,2,1,2,1]",
        "exampleOutput": "6",
        "explanation": "The elevation map traps 6 units of rain water.",
        "platformLink": "https://leetcode.com/problems/trapping-rain-water/",
        "companies_asked": ["Amazon", "Google", "Microsoft", "Facebook", "Apple"],
        "frequency_score": 0.92
    },
    {
        "id": "word-ladder",
        "title": "Word Ladder",
        "slug": "word-ladder",
        "difficulty": DSADifficulty.HARD,
        "category": "Graphs",
        "tags": ["Hash Tables", "Strings", "Breadth-First Search"],
        "description": """A transformation sequence from word beginWord to word endWord using a dictionary wordList is a sequence of words beginWord -> s1 -> s2 -> ... -> sk such that:

- Every adjacent pair of words differs by a single letter.
- Every si is in wordList. Note that beginWord does not need to be in wordList.
- sk == endWord

Given two words, beginWord and endWord, and a dictionary wordList, return the number of words in the shortest transformation sequence from beginWord to endWord, or 0 if no such sequence exists.""",
        "constraints": [
            "1 <= beginWord.length <= 10",
            "endWord.length == beginWord.length",
            "1 <= wordList.length <= 5000",
            "wordList[i].length == beginWord.length",
            "beginWord, endWord, and wordList[i] consist of lowercase English letters.",
            "beginWord != endWord",
            "All the words in wordList are unique."
        ],
        "inputFormat": "beginWord, endWord, and wordList.",
        "outputFormat": "Minimum number of transformations.",
        "exampleInput": 'beginWord = "hit", endWord = "cog", wordList = ["hot","dot","dog","lot","log","cog"]',
        "exampleOutput": "5",
        "explanation": "hit -> hot -> dot -> dog -> cog",
        "platformLink": "https://leetcode.com/problems/word-ladder/",
        "companies_asked": ["Amazon", "Google", "Facebook", "Microsoft"],
        "frequency_score": 0.85
    },
    {
        "id": "lru-cache-hard",
        "title": "LFU Cache",
        "slug": "lfu-cache",
        "difficulty": DSADifficulty.HARD,
        "category": "Algorithms",
        "tags": ["Hash Tables", "Linked List", "Design"],
        "description": """Design and implement a data structure for a Least Frequently Used (LFU) cache.

Implement the LFUCache class:
- LFUCache(int capacity) Initializes the object with the given capacity.
- int get(int key) Gets the value of the key if it exists. Otherwise, returns -1.
- void put(int key, int value) Update the value of the key if it exists. Otherwise, add the key-value pair to the cache. After modifying the key, if the cache reaches capacity, evict the least frequently used key.""",
        "constraints": [
            "1 <= capacity <= 10^4",
            "0 <= key <= 10^4",
            "0 <= value <= 10^9",
            "At most 2 * 10^5 calls will be made to get and put."
        ],
        "inputFormat": "Operations on LFU cache.",
        "outputFormat": "Values for get operations.",
        "exampleInput": '["LFUCache", "put", "put", "get", "put", "get", "put", "get", "get", "get"]\n[[2], [1, 1], [2, 2], [1], [3, 3], [2], [4, 4], [1], [3], [4]]',
        "exampleOutput": "[null, null, null, 1, null, -1, null, -1, 3, 4]",
        "explanation": "LFU cache with capacity 2.",
        "platformLink": "https://leetcode.com/problems/lfu-cache/",
        "companies_asked": ["Google", "Amazon", "Microsoft", "Facebook"],
        "frequency_score": 0.82
    },
    {
        "id": "serialize-deserialize-binary-tree",
        "title": "Serialize and Deserialize Binary Tree",
        "slug": "serialize-deserialize-binary-tree",
        "difficulty": DSADifficulty.HARD,
        "category": "Trees",
        "tags": ["Trees", "Depth-First Search", "Breadth-First Search", "Design"],
        "description": """Serialization is the process of converting a data structure or object into a sequence of bits so that it can be stored in a file or memory buffer, or transmitted across a network connection link to be reconstructed later.

Design an algorithm to serialize and deserialize a binary tree. There is no restriction on how your serialization/deserialization algorithm should work. You just need to ensure that a binary tree can be serialized to a string and this string can be deserialized to the original tree structure.""",
        "constraints": [
            "The number of nodes in the tree is in the range [0, 10^4].",
            "-1000 <= Node.val <= 1000"
        ],
        "inputFormat": "Root of binary tree.",
        "outputFormat": "Serialized string that can be deserialized back.",
        "exampleInput": "root = [1,2,3,null,null,4,5]",
        "exampleOutput": "[1,2,3,null,null,4,5]",
        "explanation": "Tree serialized and deserialized correctly.",
        "platformLink": "https://leetcode.com/problems/serialize-and-deserialize-binary-tree/",
        "companies_asked": ["Amazon", "Facebook", "Microsoft", "Google"],
        "frequency_score": 0.88
    },
    {
        "id": "merge-k-sorted-lists",
        "title": "Merge K Sorted Lists",
        "slug": "merge-k-sorted-lists",
        "difficulty": DSADifficulty.HARD,
        "category": "Linked List",
        "tags": ["Linked List", "Divide and Conquer", "Heap", "Priority Queue"],
        "description": """You are given an array of k linked-lists lists, each linked-list is sorted in ascending order.

Merge all the linked-lists into one sorted linked-list and return it.""",
        "constraints": [
            "k == lists.length",
            "0 <= k <= 10^4",
            "0 <= lists[i].length <= 500",
            "-10^4 <= lists[i][j] <= 10^4"
        ],
        "inputFormat": "Array of k sorted linked lists.",
        "outputFormat": "One merged sorted linked list.",
        "exampleInput": "lists = [[1,4,5],[1,3,4],[2,6]]",
        "exampleOutput": "[1,1,2,3,4,4,5,6]",
        "explanation": "All lists merged into one sorted list.",
        "platformLink": "https://leetcode.com/problems/merge-k-sorted-lists/",
        "companies_asked": ["Amazon", "Google", "Facebook", "Microsoft", "Apple"],
        "frequency_score": 0.90
    },
    {
        "id": "regular-expression-matching",
        "title": "Regular Expression Matching",
        "slug": "regular-expression-matching",
        "difficulty": DSADifficulty.HARD,
        "category": "Strings",
        "tags": ["Strings", "Dynamic Programming", "Recursion"],
        "description": """Given an input string s and a pattern p, implement regular expression matching with support for '.' and '*' where:
- '.' Matches any single character.
- '*' Matches zero or more of the preceding element.

The matching should cover the entire input string (not partial).""",
        "constraints": [
            "1 <= s.length <= 20",
            "1 <= p.length <= 20",
            "s contains only lowercase English letters.",
            "p contains only lowercase English letters, '.', and '*'.",
            "It is guaranteed for each appearance of '*', there will be a previous valid character to match."
        ],
        "inputFormat": "String s and pattern p.",
        "outputFormat": "True if matches, False otherwise.",
        "exampleInput": 's = "aa", p = "a*"',
        "exampleOutput": "true",
        "explanation": "'*' matches zero or more of preceding element 'a'.",
        "platformLink": "https://leetcode.com/problems/regular-expression-matching/",
        "companies_asked": ["Google", "Facebook", "Microsoft", "Amazon", "Apple"],
        "frequency_score": 0.85
    },
    {
        "id": "merge-intervals",
        "title": "Merge Intervals",
        "slug": "merge-intervals",
        "difficulty": DSADifficulty.HARD,
        "category": "Algorithms",
        "tags": ["Arrays", "Sorting"],
        "description": """Given an array of intervals where intervals[i] = [starti, endi], merge all overlapping intervals, and return an array of the non-overlapping intervals that cover all the intervals in the input.""",
        "constraints": [
            "1 <= intervals.length <= 10^4",
            "intervals[i].length == 2",
            "0 <= starti <= endi <= 10^4"
        ],
        "inputFormat": "Array of intervals.",
        "outputFormat": "Merged non-overlapping intervals.",
        "exampleInput": "intervals = [[1,3],[2,6],[8,10],[15,18]]",
        "exampleOutput": "[[1,6],[8,10],[15,18]]",
        "explanation": "Overlapping intervals are merged.",
        "platformLink": "https://leetcode.com/problems/merge-intervals/",
        "companies_asked": ["Google", "Facebook", "Microsoft", "Amazon", "Apple"],
        "frequency_score": 0.88
    }
]


def get_daily_problem() -> Dict[str, Any]:
    """Get the daily problem based on the current date."""
    from datetime import date
    
    # Use the day of year to cycle through problems
    today = date.today()
    day_of_year = (today - date(today.year, 1, 1)).days
    
    # Distribute problems by difficulty
    easy_problems = [p for p in CURATED_PROBLEMS if p["difficulty"] == DSADifficulty.EASY]
    medium_problems = [p for p in CURATED_PROBLEMS if p["difficulty"] == DSADifficulty.MEDIUM]
    hard_problems = [p for p in CURATED_PROBLEMS if p["difficulty"] == DSADifficulty.HARD]
    
    # Rotate daily based on day of week
    day_of_week = today.weekday()
    
    if day_of_week < 3:  # Monday, Tuesday, Wednesday
        problems = easy_problems
        index = day_of_week
    elif day_of_week < 5:  # Thursday, Friday
        problems = medium_problems
        index = day_of_week - 3
    else:  # Saturday, Sunday
        problems = hard_problems
        index = day_of_week - 5
    
    # Ensure we have a valid index
    if index >= len(problems):
        index = index % len(problems) if problems else 0
    
    problem = problems[index] if problems else CURATED_PROBLEMS[0]
    
    return {
        "title": problem["title"],
        "difficulty": problem["difficulty"].value,
        "category": problem["category"],
        "tags": problem["tags"],
        "platformLink": problem["platformLink"],
        "date": today.isoformat()
    }


def get_problem_by_slug(slug: str) -> Dict[str, Any]:
    """Get a specific problem by slug."""
    for problem in CURATED_PROBLEMS:
        if problem["slug"] == slug:
            return problem
    return None


def get_problems(
    difficulty: str = None,
    topic: str = None,
    search: str = None,
    limit: int = 20,
    offset: int = 0
) -> Dict[str, Any]:
    """Get problems with optional filters."""
    filtered = CURATED_PROBLEMS.copy()
    
    # Filter by difficulty
    if difficulty:
        filtered = [p for p in filtered if p["difficulty"].value == difficulty.lower()]
    
    # Filter by topic
    if topic:
        filtered = [p for p in filtered if topic.lower() in [t.lower() for t in p["tags"]]]
    
    # Search by title
    if search:
        search_lower = search.lower()
        filtered = [p for p in filtered if search_lower in p["title"].lower()]
    
    total = len(filtered)
    
    # Apply pagination
    paginated = filtered[offset:offset + limit]
    
    return {
        "problems": paginated,
        "total": total,
        "limit": limit,
        "offset": offset
    }
