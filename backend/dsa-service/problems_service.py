# # import sys, os
# # sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
# # from fastapi import FastAPI, Query
# # from fastapi.middleware.cors import CORSMiddleware
# # from typing import Optional, List, Dict, Any
# # from datetime import date
# # from enum import Enum

# # class DSADifficulty(str, Enum):
# #     EASY = "easy"
# #     MEDIUM = "medium"
# #     HARD = "hard"

# # app = FastAPI(title="DSA Practice Service", version="2.0.0")
# # app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

# # if __name__ == "__main__":
# #     import uvicorn
# #     uvicorn.run(app, host="0.0.0.0", port=8004, reload=True)



# """
# DSA Practice Service - problems_service.py
# A clean, standalone FastAPI backend for the practice page.
# Run: python problems_service.py
# Port: 8004
# """

# import sys, os
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# from fastapi import FastAPI, Query
# from fastapi.middleware.cors import CORSMiddleware
# from typing import Optional, List, Dict, Any
# from datetime import date
# from enum import Enum

# # ─────────────────────────────────────────────
# #  DATA
# # ─────────────────────────────────────────────

# class DSADifficulty(str, Enum):
#     EASY   = "easy"
#     MEDIUM = "medium"
#     HARD   = "hard"

# TOPICS = [
#     "Arrays", "Strings", "Linked List", "Trees", "Graphs",
#     "Dynamic Programming", "Recursion", "Stack", "Queue",
#     "Hash Tables", "Two Pointers", "Sliding Window",
#     "Binary Search", "Greedy", "Backtracking", "Heap",
#     "Sorting", "Divide and Conquer", "Bit Manipulation", "Math",
# ]

# PROBLEMS: List[Dict[str, Any]] = [
#     # ── EASY ──────────────────────────────────────────────────────
#     {
#         "id": "two-sum", "title": "Two Sum", "slug": "two-sum",
#         "difficulty": DSADifficulty.EASY, "category": "Arrays",
#         "tags": ["Arrays", "Hash Tables"],
#         "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.\n\nYou may assume that each input would have exactly one solution, and you may not use the same element twice.",
#         "constraints": ["2 <= nums.length <= 10^4", "-10^9 <= nums[i] <= 10^9", "Only one valid answer exists."],
#         "inputFormat": "Array of integers and a target integer.",
#         "outputFormat": "Indices of the two numbers that sum to target.",
#         "exampleInput": "nums = [2,7,11,15], target = 9",
#         "exampleOutput": "[0,1]",
#         "explanation": "nums[0] + nums[1] == 9, so return [0, 1].",
#         "platformLink": "https://leetcode.com/problems/two-sum/",
#         "companies_asked": ["Google", "Amazon", "Apple", "Microsoft", "Meta"],
#         "frequency_score": 0.95, "acceptance_rate": 49.1,
#         "hints": ["Try using a hash map to store complements.", "For each number, check if target - num exists in the map."],
#         "time_complexity": "O(n)", "space_complexity": "O(n)",
#     },
#     {
#         "id": "reverse-string", "title": "Reverse String", "slug": "reverse-string",
#         "difficulty": DSADifficulty.EASY, "category": "Strings",
#         "tags": ["Strings", "Two Pointers"],
#         "description": "Write a function that reverses a string. The input string is given as an array of characters s.\n\nYou must do this by modifying the input array in-place with O(1) extra memory.",
#         "constraints": ["1 <= s.length <= 10^5", "s[i] is a printable ascii character."],
#         "inputFormat": "Array of characters s.", "outputFormat": "Reversed array in-place.",
#         "exampleInput": 's = ["h","e","l","l","o"]', "exampleOutput": '["o","l","l","e","h"]',
#         "explanation": "Use two pointers from both ends and swap.",
#         "platformLink": "https://leetcode.com/problems/reverse-string/",
#         "companies_asked": ["Amazon", "Microsoft", "Apple"],
#         "frequency_score": 0.82, "acceptance_rate": 75.4,
#         "hints": ["Use two pointers."], "time_complexity": "O(n)", "space_complexity": "O(1)",
#     },
#     {
#         "id": "valid-parentheses", "title": "Valid Parentheses", "slug": "valid-parentheses",
#         "difficulty": DSADifficulty.EASY, "category": "Stack",
#         "tags": ["Stack", "Strings"],
#         "description": "Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.\n\nAn input string is valid if:\n1. Open brackets must be closed by the same type.\n2. Open brackets must be closed in the correct order.\n3. Every close bracket has a corresponding open bracket.",
#         "constraints": ["1 <= s.length <= 10^4", "s consists of parentheses only '()[]{}'."],
#         "inputFormat": "String of parentheses.", "outputFormat": "true or false.",
#         "exampleInput": 's = "()"', "exampleOutput": "true",
#         "explanation": "Parentheses are properly balanced.",
#         "platformLink": "https://leetcode.com/problems/valid-parentheses/",
#         "companies_asked": ["Amazon", "Google", "Meta", "Microsoft"],
#         "frequency_score": 0.90, "acceptance_rate": 40.7,
#         "hints": ["Use a stack. Push opening brackets, pop on closing."],
#         "time_complexity": "O(n)", "space_complexity": "O(n)",
#     },
#     {
#         "id": "best-time-stock", "title": "Best Time to Buy and Sell Stock", "slug": "best-time-stock",
#         "difficulty": DSADifficulty.EASY, "category": "Arrays",
#         "tags": ["Arrays", "Dynamic Programming"],
#         "description": "You are given an array prices where prices[i] is the price of a stock on the ith day.\n\nMaximize profit by choosing a single day to buy and a future day to sell. Return maximum profit or 0 if no profit is possible.",
#         "constraints": ["1 <= prices.length <= 10^5", "0 <= prices[i] <= 10^4"],
#         "inputFormat": "Array of stock prices.", "outputFormat": "Maximum profit.",
#         "exampleInput": "prices = [7,1,5,3,6,4]", "exampleOutput": "5",
#         "explanation": "Buy on day 2 (price=1), sell day 5 (price=6). Profit = 5.",
#         "platformLink": "https://leetcode.com/problems/best-time-to-buy-and-sell-stock/",
#         "companies_asked": ["Amazon", "Meta", "Microsoft", "Apple"],
#         "frequency_score": 0.88, "acceptance_rate": 54.3,
#         "hints": ["Track minimum price seen so far."],
#         "time_complexity": "O(n)", "space_complexity": "O(1)",
#     },
#     {
#         "id": "maximum-subarray", "title": "Maximum Subarray", "slug": "maximum-subarray",
#         "difficulty": DSADifficulty.EASY, "category": "Arrays",
#         "tags": ["Arrays", "Dynamic Programming", "Divide and Conquer"],
#         "description": "Given an integer array nums, find the subarray with the largest sum and return its sum.",
#         "constraints": ["1 <= nums.length <= 10^5", "-10^4 <= nums[i] <= 10^4"],
#         "inputFormat": "Array of integers.", "outputFormat": "Maximum subarray sum.",
#         "exampleInput": "nums = [-2,1,-3,4,-1,2,1,-5,4]", "exampleOutput": "6",
#         "explanation": "[4,-1,2,1] has the largest sum 6.",
#         "platformLink": "https://leetcode.com/problems/maximum-subarray/",
#         "companies_asked": ["Amazon", "Microsoft", "Apple", "LinkedIn"],
#         "frequency_score": 0.92, "acceptance_rate": 49.8,
#         "hints": ["Kadane's algorithm: track current sum and max sum."],
#         "time_complexity": "O(n)", "space_complexity": "O(1)",
#     },
#     {
#         "id": "valid-palindrome", "title": "Valid Palindrome", "slug": "valid-palindrome",
#         "difficulty": DSADifficulty.EASY, "category": "Strings",
#         "tags": ["Strings", "Two Pointers"],
#         "description": "A phrase is a palindrome if, after converting to lowercase and removing non-alphanumeric characters, it reads the same forward and backward.\n\nGiven string s, return true if it is a palindrome.",
#         "constraints": ["1 <= s.length <= 2*10^5"],
#         "inputFormat": "String s.", "outputFormat": "true or false.",
#         "exampleInput": 's = "A man, a plan, a canal: Panama"', "exampleOutput": "true",
#         "explanation": '"amanaplanacanalpanama" is a palindrome.',
#         "platformLink": "https://leetcode.com/problems/valid-palindrome/",
#         "companies_asked": ["Meta", "Microsoft", "Amazon"],
#         "frequency_score": 0.78, "acceptance_rate": 43.1,
#         "hints": ["Use two pointers from both ends, skip non-alphanumeric."],
#         "time_complexity": "O(n)", "space_complexity": "O(1)",
#     },
#     {
#         "id": "linked-list-cycle", "title": "Linked List Cycle", "slug": "linked-list-cycle",
#         "difficulty": DSADifficulty.EASY, "category": "Linked List",
#         "tags": ["Linked List", "Two Pointers", "Hash Tables"],
#         "description": "Given head of a linked list, determine if the linked list has a cycle.\n\nReturn true if there is a cycle, otherwise false.",
#         "constraints": ["0 <= number of nodes <= 10^4", "-10^5 <= Node.val <= 10^5"],
#         "inputFormat": "Head of a linked list.", "outputFormat": "true or false.",
#         "exampleInput": "head = [3,2,0,-4], pos = 1", "exampleOutput": "true",
#         "explanation": "Tail connects to node at index 1.",
#         "platformLink": "https://leetcode.com/problems/linked-list-cycle/",
#         "companies_asked": ["Amazon", "Google", "Microsoft", "Apple"],
#         "frequency_score": 0.82, "acceptance_rate": 46.5,
#         "hints": ["Floyd's cycle detection — slow and fast pointers."],
#         "time_complexity": "O(n)", "space_complexity": "O(1)",
#     },
#     {
#         "id": "merge-sorted-array", "title": "Merge Sorted Array", "slug": "merge-sorted-array",
#         "difficulty": DSADifficulty.EASY, "category": "Arrays",
#         "tags": ["Arrays", "Two Pointers", "Sorting"],
#         "description": "Given two sorted integer arrays nums1 and nums2, merge nums2 into nums1 as one sorted array in-place.",
#         "constraints": ["nums1.length == m + n", "0 <= m, n <= 200"],
#         "inputFormat": "Two sorted arrays nums1, nums2 and sizes m, n.", "outputFormat": "Merged sorted array in nums1.",
#         "exampleInput": "nums1 = [1,2,3,0,0,0], m = 3, nums2 = [2,5,6], n = 3", "exampleOutput": "[1,2,2,3,5,6]",
#         "explanation": "Merge from the end to avoid overwriting.",
#         "platformLink": "https://leetcode.com/problems/merge-sorted-array/",
#         "companies_asked": ["Amazon", "Microsoft", "Google"],
#         "frequency_score": 0.75, "acceptance_rate": 47.0,
#         "hints": ["Start filling from the end of nums1."],
#         "time_complexity": "O(m+n)", "space_complexity": "O(1)",
#     },
#     {
#         "id": "climbing-stairs", "title": "Climbing Stairs", "slug": "climbing-stairs",
#         "difficulty": DSADifficulty.EASY, "category": "Dynamic Programming",
#         "tags": ["Dynamic Programming", "Math", "Recursion"],
#         "description": "You are climbing a staircase. It takes n steps to reach the top. Each time you can climb 1 or 2 steps. How many distinct ways can you climb to the top?",
#         "constraints": ["1 <= n <= 45"],
#         "inputFormat": "Integer n.", "outputFormat": "Number of distinct ways.",
#         "exampleInput": "n = 3", "exampleOutput": "3",
#         "explanation": "1+1+1, 1+2, 2+1 — three ways.",
#         "platformLink": "https://leetcode.com/problems/climbing-stairs/",
#         "companies_asked": ["Amazon", "Google", "Apple", "Adobe"],
#         "frequency_score": 0.87, "acceptance_rate": 51.7,
#         "hints": ["This is essentially Fibonacci."],
#         "time_complexity": "O(n)", "space_complexity": "O(1)",
#     },
#     {
#         "id": "binary-search", "title": "Binary Search", "slug": "binary-search",
#         "difficulty": DSADifficulty.EASY, "category": "Arrays",
#         "tags": ["Arrays", "Binary Search"],
#         "description": "Given an array of integers nums sorted in ascending order, and an integer target, write a function to search target in nums. If target exists, return its index. Otherwise, return -1.",
#         "constraints": ["1 <= nums.length <= 10^4", "All nums are unique.", "nums is sorted ascending."],
#         "inputFormat": "Sorted array nums and target integer.", "outputFormat": "Index of target or -1.",
#         "exampleInput": "nums = [-1,0,3,5,9,12], target = 9", "exampleOutput": "4",
#         "explanation": "9 exists at index 4.",
#         "platformLink": "https://leetcode.com/problems/binary-search/",
#         "companies_asked": ["Google", "Amazon", "Microsoft"],
#         "frequency_score": 0.80, "acceptance_rate": 55.6,
#         "hints": ["Use left and right pointers. Mid = (l+r)//2."],
#         "time_complexity": "O(log n)", "space_complexity": "O(1)",
#     },

#     # ── MEDIUM ─────────────────────────────────────────────────────
#     {
#         "id": "longest-substring", "title": "Longest Substring Without Repeating Characters", "slug": "longest-substring",
#         "difficulty": DSADifficulty.MEDIUM, "category": "Strings",
#         "tags": ["Hash Tables", "Strings", "Sliding Window"],
#         "description": "Given a string s, find the length of the longest substring without repeating characters.",
#         "constraints": ["0 <= s.length <= 5*10^4"],
#         "inputFormat": "String s.", "outputFormat": "Length of longest substring.",
#         "exampleInput": 's = "abcabcbb"', "exampleOutput": "3",
#         "explanation": '"abc" is the answer with length 3.',
#         "platformLink": "https://leetcode.com/problems/longest-substring-without-repeating-characters/",
#         "companies_asked": ["Amazon", "Google", "Meta", "Microsoft", "Apple"],
#         "frequency_score": 0.95, "acceptance_rate": 33.8,
#         "hints": ["Use a sliding window with a set.", "Expand right, shrink left when duplicate found."],
#         "time_complexity": "O(n)", "space_complexity": "O(min(m,n))",
#     },
#     {
#         "id": "3sum", "title": "3Sum", "slug": "3sum",
#         "difficulty": DSADifficulty.MEDIUM, "category": "Arrays",
#         "tags": ["Arrays", "Two Pointers", "Sorting"],
#         "description": "Given an integer array nums, return all the triplets [nums[i], nums[j], nums[k]] such that i != j != k, and nums[i] + nums[j] + nums[k] == 0. Solution set must not contain duplicate triplets.",
#         "constraints": ["0 <= nums.length <= 3000", "-10^5 <= nums[i] <= 10^5"],
#         "inputFormat": "Array of integers.", "outputFormat": "List of unique triplets summing to zero.",
#         "exampleInput": "nums = [-1,0,1,2,-1,-4]", "exampleOutput": "[[-1,-1,2],[-1,0,1]]",
#         "explanation": "Sort, then use two pointers for each element.",
#         "platformLink": "https://leetcode.com/problems/3sum/",
#         "companies_asked": ["Amazon", "Meta", "Google", "Microsoft", "Apple"],
#         "frequency_score": 0.92, "acceptance_rate": 32.0,
#         "hints": ["Sort the array first.", "For each element, use two pointers on the rest."],
#         "time_complexity": "O(n²)", "space_complexity": "O(n)",
#     },
#     {
#         "id": "container-water", "title": "Container With Most Water", "slug": "container-water",
#         "difficulty": DSADifficulty.MEDIUM, "category": "Arrays",
#         "tags": ["Arrays", "Two Pointers", "Greedy"],
#         "description": "Given integer array height of length n, find two lines that form a container holding the most water. Return the maximum amount of water.",
#         "constraints": ["2 <= n <= 10^5", "0 <= height[i] <= 10^4"],
#         "inputFormat": "Array of heights.", "outputFormat": "Maximum water.",
#         "exampleInput": "height = [1,8,6,2,5,4,8,3,7]", "exampleOutput": "49",
#         "explanation": "Two pointers from ends, always move the shorter one inward.",
#         "platformLink": "https://leetcode.com/problems/container-with-most-water/",
#         "companies_asked": ["Amazon", "Google", "Microsoft", "Meta"],
#         "frequency_score": 0.88, "acceptance_rate": 54.0,
#         "hints": ["Greedy two-pointer approach.", "Moving the taller line can only decrease area."],
#         "time_complexity": "O(n)", "space_complexity": "O(1)",
#     },
#     {
#         "id": "coin-change", "title": "Coin Change", "slug": "coin-change",
#         "difficulty": DSADifficulty.MEDIUM, "category": "Dynamic Programming",
#         "tags": ["Dynamic Programming", "Arrays", "Greedy"],
#         "description": "Given integer array coins and integer amount, return the fewest coins needed to make up amount. Return -1 if not possible. You have infinite coins of each denomination.",
#         "constraints": ["1 <= coins.length <= 12", "0 <= amount <= 10^4"],
#         "inputFormat": "Array of coin denominations and target amount.", "outputFormat": "Minimum coins or -1.",
#         "exampleInput": "coins = [1,2,5], amount = 11", "exampleOutput": "3",
#         "explanation": "11 = 5 + 5 + 1",
#         "platformLink": "https://leetcode.com/problems/coin-change/",
#         "companies_asked": ["Amazon", "Google", "Apple", "Meta"],
#         "frequency_score": 0.90, "acceptance_rate": 41.5,
#         "hints": ["Build dp array from 0 to amount.", "dp[i] = min coins to make i."],
#         "time_complexity": "O(amount × coins)", "space_complexity": "O(amount)",
#     },
#     {
#         "id": "number-of-islands", "title": "Number of Islands", "slug": "number-of-islands",
#         "difficulty": DSADifficulty.MEDIUM, "category": "Graphs",
#         "tags": ["Graphs", "Depth-First Search", "Breadth-First Search"],
#         "description": "Given an m×n 2D binary grid of '1's (land) and '0's (water), return the number of islands. An island is formed by connecting adjacent lands horizontally or vertically.",
#         "constraints": ["1 <= m, n <= 300", "grid[i][j] is '0' or '1'."],
#         "inputFormat": "2D grid of '1's and '0's.", "outputFormat": "Number of islands.",
#         "exampleInput": "grid = [['1','1','0'],['0','1','0'],['0','0','1']]", "exampleOutput": "2",
#         "explanation": "DFS/BFS flood-fill each island.",
#         "platformLink": "https://leetcode.com/problems/number-of-islands/",
#         "companies_asked": ["Amazon", "Meta", "Microsoft", "Google", "Apple"],
#         "frequency_score": 0.87, "acceptance_rate": 57.5,
#         "hints": ["DFS or BFS from every unvisited '1'.", "Mark visited cells as '0'."],
#         "time_complexity": "O(m×n)", "space_complexity": "O(m×n)",
#     },
#     {
#         "id": "validate-bst", "title": "Validate Binary Search Tree", "slug": "validate-bst",
#         "difficulty": DSADifficulty.MEDIUM, "category": "Trees",
#         "tags": ["Trees", "Depth-First Search", "Binary Search"],
#         "description": "Given the root of a binary tree, determine if it is a valid BST.\n\nA valid BST requires: left subtree values < node key, right subtree values > node key, both subtrees must also be valid BSTs.",
#         "constraints": ["1 <= nodes <= 10^4", "-2^31 <= Node.val <= 2^31-1"],
#         "inputFormat": "Root of binary tree.", "outputFormat": "true or false.",
#         "exampleInput": "root = [2,1,3]", "exampleOutput": "true",
#         "explanation": "Pass min/max bounds down the recursion.",
#         "platformLink": "https://leetcode.com/problems/validate-binary-search-tree/",
#         "companies_asked": ["Amazon", "Meta", "Microsoft", "Bloomberg"],
#         "frequency_score": 0.85, "acceptance_rate": 31.8,
#         "hints": ["Pass valid range (min, max) to each node.", "Root has range (-inf, +inf)."],
#         "time_complexity": "O(n)", "space_complexity": "O(n)",
#     },
#     {
#         "id": "lru-cache", "title": "LRU Cache", "slug": "lru-cache",
#         "difficulty": DSADifficulty.MEDIUM, "category": "Hash Tables",
#         "tags": ["Hash Tables", "Linked List", "Design"],
#         "description": "Design an LRU (Least Recently Used) cache.\n\nImplement: LRUCache(capacity), get(key) → value or -1, put(key, value) — evict LRU when capacity exceeded.",
#         "constraints": ["1 <= capacity <= 3000", "At most 2×10^5 calls to get and put."],
#         "inputFormat": "Operations on LRU cache.", "outputFormat": "Values for get operations.",
#         "exampleInput": '["LRUCache","put","put","get"]\n[[2],[1,1],[2,2],[1]]', "exampleOutput": "[null,null,null,1]",
#         "explanation": "Combine HashMap + Doubly Linked List for O(1) get and put.",
#         "platformLink": "https://leetcode.com/problems/lru-cache/",
#         "companies_asked": ["Amazon", "Google", "Microsoft", "Meta", "Apple"],
#         "frequency_score": 0.88, "acceptance_rate": 40.6,
#         "hints": ["Use OrderedDict in Python.", "Or HashMap + doubly linked list manually."],
#         "time_complexity": "O(1)", "space_complexity": "O(capacity)",
#     },
#     {
#         "id": "word-search", "title": "Word Search", "slug": "word-search",
#         "difficulty": DSADifficulty.MEDIUM, "category": "Backtracking",
#         "tags": ["Backtracking", "Graphs", "Depth-First Search"],
#         "description": "Given an m×n grid of characters and a string word, return true if word exists in the grid.\n\nThe word can be constructed from sequentially adjacent cells (horizontally or vertically). A cell cannot be reused.",
#         "constraints": ["1 <= m, n <= 6", "1 <= word.length <= 15"],
#         "inputFormat": "2D grid and word string.", "outputFormat": "true or false.",
#         "exampleInput": 'board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], word = "ABCCED"', "exampleOutput": "true",
#         "explanation": "DFS with backtracking — mark visited, unmark on backtrack.",
#         "platformLink": "https://leetcode.com/problems/word-search/",
#         "companies_asked": ["Amazon", "Microsoft", "Google", "Bloomberg"],
#         "frequency_score": 0.83, "acceptance_rate": 40.7,
#         "hints": ["DFS from every cell.", "Mark visited cells temporarily."],
#         "time_complexity": "O(m×n×4^L)", "space_complexity": "O(L)",
#     },
#     {
#         "id": "product-except-self", "title": "Product of Array Except Self", "slug": "product-except-self",
#         "difficulty": DSADifficulty.MEDIUM, "category": "Arrays",
#         "tags": ["Arrays", "Two Pointers"],
#         "description": "Given integer array nums, return array answer where answer[i] is the product of all elements except nums[i]. Must run in O(n) time without division.",
#         "constraints": ["2 <= nums.length <= 10^5", "-30 <= nums[i] <= 30"],
#         "inputFormat": "Array of integers.", "outputFormat": "Product array.",
#         "exampleInput": "nums = [1,2,3,4]", "exampleOutput": "[24,12,8,6]",
#         "explanation": "Prefix product pass then suffix product pass.",
#         "platformLink": "https://leetcode.com/problems/product-of-array-except-self/",
#         "companies_asked": ["Amazon", "Microsoft", "Apple", "Google", "Meta"],
#         "frequency_score": 0.89, "acceptance_rate": 64.4,
#         "hints": ["Two passes: prefix products left-to-right, suffix products right-to-left."],
#         "time_complexity": "O(n)", "space_complexity": "O(1)",
#     },
#     {
#         "id": "spiral-matrix", "title": "Spiral Matrix", "slug": "spiral-matrix",
#         "difficulty": DSADifficulty.MEDIUM, "category": "Arrays",
#         "tags": ["Arrays", "Sorting", "Simulation"],
#         "description": "Given an m×n matrix, return all elements in spiral order.",
#         "constraints": ["1 <= m, n <= 10"],
#         "inputFormat": "2D matrix.", "outputFormat": "Elements in spiral order.",
#         "exampleInput": "matrix = [[1,2,3],[4,5,6],[7,8,9]]", "exampleOutput": "[1,2,3,6,9,8,7,4,5]",
#         "explanation": "Maintain top, bottom, left, right boundaries and shrink after each pass.",
#         "platformLink": "https://leetcode.com/problems/spiral-matrix/",
#         "companies_asked": ["Microsoft", "Amazon", "Apple", "Google"],
#         "frequency_score": 0.76, "acceptance_rate": 44.8,
#         "hints": ["Track four boundaries and move them inward."],
#         "time_complexity": "O(m×n)", "space_complexity": "O(1)",
#     },
#     {
#         "id": "binary-tree-zigzag", "title": "Binary Tree Zigzag Level Order Traversal", "slug": "binary-tree-zigzag",
#         "difficulty": DSADifficulty.MEDIUM, "category": "Trees",
#         "tags": ["Trees", "Breadth-First Search", "Queue"],
#         "description": "Given root of a binary tree, return the zigzag level order traversal of its nodes' values (left to right, then right to left for next level, alternating).",
#         "constraints": ["0 <= nodes <= 2000", "-100 <= Node.val <= 100"],
#         "inputFormat": "Root of binary tree.", "outputFormat": "Zigzag level order list of lists.",
#         "exampleInput": "root = [3,9,20,null,null,15,7]", "exampleOutput": "[[3],[20,9],[15,7]]",
#         "explanation": "BFS level-by-level, reverse alternate levels.",
#         "platformLink": "https://leetcode.com/problems/binary-tree-zigzag-level-order-traversal/",
#         "companies_asked": ["Amazon", "Bloomberg", "Meta"],
#         "frequency_score": 0.77, "acceptance_rate": 56.0,
#         "hints": ["Standard BFS but toggle direction each level."],
#         "time_complexity": "O(n)", "space_complexity": "O(n)",
#     },

#     # ── HARD ───────────────────────────────────────────────────────
#     {
#         "id": "median-two-arrays", "title": "Median of Two Sorted Arrays", "slug": "median-two-arrays",
#         "difficulty": DSADifficulty.HARD, "category": "Arrays",
#         "tags": ["Arrays", "Binary Search", "Divide and Conquer"],
#         "description": "Given two sorted arrays nums1 and nums2 of size m and n, return the median of the two sorted arrays. The overall run time complexity should be O(log(m+n)).",
#         "constraints": ["0 <= m, n <= 1000", "1 <= m+n <= 2000", "-10^6 <= nums[i] <= 10^6"],
#         "inputFormat": "Two sorted arrays.", "outputFormat": "Median as float.",
#         "exampleInput": "nums1 = [1,3], nums2 = [2]", "exampleOutput": "2.00000",
#         "explanation": "Binary search on the smaller array to find the correct partition.",
#         "platformLink": "https://leetcode.com/problems/median-of-two-sorted-arrays/",
#         "companies_asked": ["Amazon", "Google", "Microsoft", "Apple", "Meta"],
#         "frequency_score": 0.95, "acceptance_rate": 37.9,
#         "hints": ["Binary search on the smaller array.", "Ensure left half total == right half total."],
#         "time_complexity": "O(log(min(m,n)))", "space_complexity": "O(1)",
#     },
#     {
#         "id": "trapping-rain-water", "title": "Trapping Rain Water", "slug": "trapping-rain-water",
#         "difficulty": DSADifficulty.HARD, "category": "Arrays",
#         "tags": ["Arrays", "Two Pointers", "Dynamic Programming", "Stack"],
#         "description": "Given n non-negative integers representing an elevation map where the width of each bar is 1, compute how much water it can trap after raining.",
#         "constraints": ["n == height.length", "1 <= n <= 2×10^4", "0 <= height[i] <= 10^5"],
#         "inputFormat": "Array of elevations.", "outputFormat": "Total water trapped.",
#         "exampleInput": "height = [0,1,0,2,1,0,1,3,2,1,2,1]", "exampleOutput": "6",
#         "explanation": "Two pointer: track left_max and right_max, add min - height[i].",
#         "platformLink": "https://leetcode.com/problems/trapping-rain-water/",
#         "companies_asked": ["Amazon", "Google", "Microsoft", "Meta", "Apple"],
#         "frequency_score": 0.92, "acceptance_rate": 60.7,
#         "hints": ["Two pointers: left_max from left, right_max from right."],
#         "time_complexity": "O(n)", "space_complexity": "O(1)",
#     },
#     {
#         "id": "merge-k-lists", "title": "Merge K Sorted Lists", "slug": "merge-k-lists",
#         "difficulty": DSADifficulty.HARD, "category": "Linked List",
#         "tags": ["Linked List", "Divide and Conquer", "Heap"],
#         "description": "You are given an array of k linked-lists, each sorted in ascending order. Merge all linked-lists into one sorted linked-list and return it.",
#         "constraints": ["k == lists.length", "0 <= k <= 10^4", "-10^4 <= lists[i][j] <= 10^4"],
#         "inputFormat": "Array of k sorted linked lists.", "outputFormat": "One merged sorted linked list.",
#         "exampleInput": "lists = [[1,4,5],[1,3,4],[2,6]]", "exampleOutput": "[1,1,2,3,4,4,5,6]",
#         "explanation": "Use min-heap of size k, always extract minimum.",
#         "platformLink": "https://leetcode.com/problems/merge-k-sorted-lists/",
#         "companies_asked": ["Amazon", "Google", "Meta", "Microsoft", "Apple"],
#         "frequency_score": 0.90, "acceptance_rate": 49.5,
#         "hints": ["Min-heap stores (val, index, node).", "Or divide and conquer merging pairs."],
#         "time_complexity": "O(N log k)", "space_complexity": "O(k)",
#     },
#     {
#         "id": "word-ladder", "title": "Word Ladder", "slug": "word-ladder",
#         "difficulty": DSADifficulty.HARD, "category": "Graphs",
#         "tags": ["Graphs", "Breadth-First Search", "Hash Tables", "Strings"],
#         "description": "A transformation sequence from beginWord to endWord uses a dictionary wordList where each step changes exactly one letter and the new word must be in wordList.\n\nReturn the number of words in the shortest transformation sequence, or 0 if none exists.",
#         "constraints": ["1 <= beginWord.length <= 10", "1 <= wordList.length <= 5000"],
#         "inputFormat": "beginWord, endWord, and wordList.", "outputFormat": "Minimum transformation steps or 0.",
#         "exampleInput": 'beginWord = "hit", endWord = "cog", wordList = ["hot","dot","dog","lot","log","cog"]', "exampleOutput": "5",
#         "explanation": "BFS layer by layer. For each word try all one-letter mutations.",
#         "platformLink": "https://leetcode.com/problems/word-ladder/",
#         "companies_asked": ["Amazon", "Google", "Meta", "Microsoft"],
#         "frequency_score": 0.85, "acceptance_rate": 37.6,
#         "hints": ["BFS on word graph.", "For each position try all 26 letters."],
#         "time_complexity": "O(M²×N)", "space_complexity": "O(M²×N)",
#     },
#     {
#         "id": "serialize-tree", "title": "Serialize and Deserialize Binary Tree", "slug": "serialize-tree",
#         "difficulty": DSADifficulty.HARD, "category": "Trees",
#         "tags": ["Trees", "Depth-First Search", "Breadth-First Search", "Design"],
#         "description": "Design an algorithm to serialize and deserialize a binary tree. There is no restriction on how the algorithm should work — just ensure a tree can be serialized to a string and deserialized back.",
#         "constraints": ["0 <= nodes <= 10^4", "-1000 <= Node.val <= 1000"],
#         "inputFormat": "Root of binary tree.", "outputFormat": "Serialized string, deserializable back.",
#         "exampleInput": "root = [1,2,3,null,null,4,5]", "exampleOutput": "[1,2,3,null,null,4,5]",
#         "explanation": "BFS level-order with null markers, or DFS preorder.",
#         "platformLink": "https://leetcode.com/problems/serialize-and-deserialize-binary-tree/",
#         "companies_asked": ["Amazon", "Meta", "Microsoft", "Google"],
#         "frequency_score": 0.88, "acceptance_rate": 55.0,
#         "hints": ["Use preorder DFS with 'null' for missing nodes."],
#         "time_complexity": "O(n)", "space_complexity": "O(n)",
#     },
#     {
#         "id": "regular-expression", "title": "Regular Expression Matching", "slug": "regular-expression",
#         "difficulty": DSADifficulty.HARD, "category": "Dynamic Programming",
#         "tags": ["Dynamic Programming", "Strings", "Recursion"],
#         "description": "Implement regex matching with '.' (any single char) and '*' (zero or more of preceding). The matching must cover the entire input string.",
#         "constraints": ["1 <= s.length <= 20", "1 <= p.length <= 20"],
#         "inputFormat": "String s and pattern p.", "outputFormat": "true or false.",
#         "exampleInput": 's = "aa", p = "a*"', "exampleOutput": "true",
#         "explanation": "2D DP: dp[i][j] = s[:i] matches p[:j].",
#         "platformLink": "https://leetcode.com/problems/regular-expression-matching/",
#         "companies_asked": ["Google", "Meta", "Microsoft", "Amazon", "Apple"],
#         "frequency_score": 0.85, "acceptance_rate": 28.2,
#         "hints": ["2D DP.", "Handle '*' as: zero occurrences OR one more of preceding."],
#         "time_complexity": "O(m×n)", "space_complexity": "O(m×n)",
#     },
# ]

# # ─────────────────────────────────────────────
# #  HELPER FUNCTIONS
# # ─────────────────────────────────────────────

# def get_daily_problem() -> Dict[str, Any]:
#     today = date.today()
#     idx = (today - date(today.year, 1, 1)).days % len(PROBLEMS)
#     p = PROBLEMS[idx]
#     return {
#         "id": p["id"], "title": p["title"], "slug": p["slug"],
#         "difficulty": p["difficulty"].value,
#         "category": p["category"], "tags": p["tags"],
#         "platformLink": p["platformLink"],
#         "time_complexity": p.get("time_complexity", ""),
#         "acceptance_rate": p.get("acceptance_rate", 0),
#         "date": today.isoformat(),
#     }

# def filter_and_paginate(
#     difficulty: Optional[str],
#     topic: Optional[str],
#     search: Optional[str],
#     company: Optional[str],
#     limit: int,
#     offset: int,
#     sort_by: str,
# ) -> Dict[str, Any]:
#     result = list(PROBLEMS)

#     if difficulty:
#         result = [p for p in result if p["difficulty"].value == difficulty.lower()]
#     if topic:
#         result = [p for p in result if topic in p["tags"] or topic == p["category"]]
#     if search:
#         s = search.lower()
#         result = [p for p in result if s in p["title"].lower() or s in p["category"].lower()
#                   or any(s in t.lower() for t in p["tags"])]
#     if company:
#         result = [p for p in result if company in p.get("companies_asked", [])]

#     # sort
#     if sort_by == "frequency":
#         result.sort(key=lambda x: x.get("frequency_score", 0), reverse=True)
#     elif sort_by == "acceptance":
#         result.sort(key=lambda x: x.get("acceptance_rate", 0), reverse=True)
#     elif sort_by == "difficulty_asc":
#         order = {"easy": 0, "medium": 1, "hard": 2}
#         result.sort(key=lambda x: order.get(x["difficulty"].value, 1))
#     elif sort_by == "difficulty_desc":
#         order = {"easy": 0, "medium": 1, "hard": 2}
#         result.sort(key=lambda x: order.get(x["difficulty"].value, 1), reverse=True)

#     total = len(result)
#     paginated = result[offset: offset + limit]

#     return {
#         "problems": [_serialize(p) for p in paginated],
#         "total": total,
#         "limit": limit,
#         "offset": offset,
#     }

# def _serialize(p: Dict) -> Dict:
#     return {
#         "id": p["id"], "title": p["title"], "slug": p["slug"],
#         "difficulty": p["difficulty"].value,
#         "category": p["category"], "tags": p["tags"],
#         "platformLink": p["platformLink"],
#         "companies_asked": p.get("companies_asked", []),
#         "frequency_score": p.get("frequency_score", 0),
#         "acceptance_rate": p.get("acceptance_rate", 0),
#         "time_complexity": p.get("time_complexity", ""),
#         "space_complexity": p.get("space_complexity", ""),
#     }

# def _serialize_full(p: Dict) -> Dict:
#     d = _serialize(p)
#     d.update({
#         "description": p.get("description", ""),
#         "constraints": p.get("constraints", []),
#         "inputFormat": p.get("inputFormat", ""),
#         "outputFormat": p.get("outputFormat", ""),
#         "exampleInput": p.get("exampleInput", ""),
#         "exampleOutput": p.get("exampleOutput", ""),
#         "explanation": p.get("explanation", ""),
#         "hints": p.get("hints", []),
#     })
#     return d

# # ─────────────────────────────────────────────
# #  FASTAPI APP
# # ─────────────────────────────────────────────

# app = FastAPI(title="DSA Practice Service", version="2.0.0")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=False,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @app.get("/api/problems")
# async def list_problems(
#     difficulty: Optional[str] = None,
#     topic:      Optional[str] = None,
#     search:     Optional[str] = None,
#     company:    Optional[str] = None,
#     sort_by:    str           = Query("frequency", enum=["frequency","acceptance","difficulty_asc","difficulty_desc"]),
#     limit:      int           = Query(20, ge=1, le=100),
#     offset:     int           = Query(0, ge=0),
# ):
#     return filter_and_paginate(difficulty, topic, search, company, limit, offset, sort_by)

# @app.get("/api/problems/{slug}")
# async def get_problem(slug: str):
#     p = next((x for x in PROBLEMS if x["slug"] == slug), None)
#     if not p:
#         from fastapi import HTTPException
#         raise HTTPException(404, "Problem not found")
#     return _serialize_full(p)

# @app.get("/api/daily-problem")
# async def daily_problem():
#     return get_daily_problem()

# @app.get("/api/topics")
# async def get_topics():
#     return {"topics": TOPICS}

# @app.get("/api/difficulties")
# async def get_difficulties():
#     easy   = sum(1 for p in PROBLEMS if p["difficulty"] == DSADifficulty.EASY)
#     medium = sum(1 for p in PROBLEMS if p["difficulty"] == DSADifficulty.MEDIUM)
#     hard   = sum(1 for p in PROBLEMS if p["difficulty"] == DSADifficulty.HARD)
#     return {"difficulties": [
#         {"value": "easy",   "label": "Easy",   "count": easy},
#         {"value": "medium", "label": "Medium", "count": medium},
#         {"value": "hard",   "label": "Hard",   "count": hard},
#     ]}

# @app.get("/api/companies")
# async def get_companies():
#     seen, companies = set(), []
#     for p in PROBLEMS:
#         for c in p.get("companies_asked", []):
#             if c not in seen:
#                 seen.add(c); companies.append(c)
#     return {"companies": sorted(companies)}

# @app.get("/api/stats")
# async def get_stats():
#     return {
#         "total": len(PROBLEMS),
#         "easy":   sum(1 for p in PROBLEMS if p["difficulty"] == DSADifficulty.EASY),
#         "medium": sum(1 for p in PROBLEMS if p["difficulty"] == DSADifficulty.MEDIUM),
#         "hard":   sum(1 for p in PROBLEMS if p["difficulty"] == DSADifficulty.HARD),
#         "topics": len(TOPICS),
#         "companies": len({c for p in PROBLEMS for c in p.get("companies_asked", [])}),
#     }

# @app.get("/health")
# async def health():
#     return {"status": "healthy", "service": "dsa-practice", "problems": len(PROBLEMS)}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8004, reload=True)
"""
DSA Practice Service - problems_service.py
Fetches real problems from LeetCode's public GraphQL API in real-time.
Run: python -m uvicorn problems_service:app --host 0.0.0.0 --port 8004
Port: 8004
"""
"""
DSA Practice Service - problems_service.py
Fetches real problems from LeetCode's public GraphQL API in real-time.
Run: python -m uvicorn problems_service:app --host 0.0.0.0 --port 8004
Port: 8004
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import httpx
import asyncio
import re
import json
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum

# ─────────────────────────────────────────────
#  LEETCODE API CONFIG
# ─────────────────────────────────────────────

LEETCODE_GRAPHQL = "https://leetcode.com/graphql"

HEADERS = {
    "Content-Type": "application/json",
    "Referer": "https://leetcode.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

# ─────────────────────────────────────────────
#  IN-MEMORY CACHE
# ─────────────────────────────────────────────

cache: Dict[str, Any] = {
    "problem_details": {},
    "problems_list": {},
    "daily": None,
    "daily_time": None,
}

CACHE_TTL = 3600  # 1 hour

def is_fresh(key: str) -> bool:
    t = cache.get(f"{key}_time")
    if not t:
        return False
    return (datetime.utcnow() - t).total_seconds() < CACHE_TTL

# ─────────────────────────────────────────────
#  GRAPHQL QUERIES
# ─────────────────────────────────────────────

PROBLEMS_QUERY = """
query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
  problemsetQuestionList: questionList(
    categorySlug: $categorySlug
    limit: $limit
    skip: $skip
    filters: $filters
  ) {
    total: totalNum
    questions: data {
      acRate
      difficulty
      freqBar
      frontendQuestionId: questionFrontendId
      paidOnly: isPaidOnly
      title
      titleSlug
      topicTags { name slug }
    }
  }
}
"""

DETAIL_QUERY = """
query questionData($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    questionFrontendId
    title
    titleSlug
    content
    difficulty
    topicTags { name slug }
    hints
    stats
    exampleTestcases
    isPaidOnly
  }
}
"""

DAILY_QUERY = """
query questionOfToday {
  activeDailyCodingChallengeQuestion {
    date
    link
    question {
      acRate
      difficulty
      frontendQuestionId: questionFrontendId
      paidOnly: isPaidOnly
      title
      titleSlug
      topicTags { name }
    }
  }
}
"""

# ─────────────────────────────────────────────
#  FALLBACK DATA (when LeetCode API is blocked)
# ─────────────────────────────────────────────

FALLBACK_PROBLEMS = [
    {"titleSlug":"two-sum","title":"Two Sum","difficulty":"Easy","acRate":49.1,"topicTags":[{"name":"Array"},{"name":"Hash Table"}],"frontendQuestionId":"1","paidOnly":False},
    {"titleSlug":"palindrome-number","title":"Palindrome Number","difficulty":"Easy","acRate":53.7,"topicTags":[{"name":"Math"}],"frontendQuestionId":"9","paidOnly":False},
    {"titleSlug":"roman-to-integer","title":"Roman to Integer","difficulty":"Easy","acRate":58.4,"topicTags":[{"name":"Hash Table"},{"name":"String"}],"frontendQuestionId":"13","paidOnly":False},
    {"titleSlug":"valid-parentheses","title":"Valid Parentheses","difficulty":"Easy","acRate":40.7,"topicTags":[{"name":"Stack"},{"name":"String"}],"frontendQuestionId":"20","paidOnly":False},
    {"titleSlug":"merge-two-sorted-lists","title":"Merge Two Sorted Lists","difficulty":"Easy","acRate":62.7,"topicTags":[{"name":"Linked List"},{"name":"Recursion"}],"frontendQuestionId":"21","paidOnly":False},
    {"titleSlug":"maximum-subarray","title":"Maximum Subarray","difficulty":"Easy","acRate":49.8,"topicTags":[{"name":"Array"},{"name":"Dynamic Programming"}],"frontendQuestionId":"53","paidOnly":False},
    {"titleSlug":"climbing-stairs","title":"Climbing Stairs","difficulty":"Easy","acRate":51.7,"topicTags":[{"name":"Dynamic Programming"},{"name":"Math"}],"frontendQuestionId":"70","paidOnly":False},
    {"titleSlug":"best-time-to-buy-and-sell-stock","title":"Best Time to Buy and Sell Stock","difficulty":"Easy","acRate":54.3,"topicTags":[{"name":"Array"},{"name":"Dynamic Programming"}],"frontendQuestionId":"121","paidOnly":False},
    {"titleSlug":"valid-palindrome","title":"Valid Palindrome","difficulty":"Easy","acRate":43.1,"topicTags":[{"name":"String"},{"name":"Two Pointers"}],"frontendQuestionId":"125","paidOnly":False},
    {"titleSlug":"linked-list-cycle","title":"Linked List Cycle","difficulty":"Easy","acRate":46.5,"topicTags":[{"name":"Linked List"},{"name":"Two Pointers"}],"frontendQuestionId":"141","paidOnly":False},
    {"titleSlug":"binary-search","title":"Binary Search","difficulty":"Easy","acRate":55.6,"topicTags":[{"name":"Array"},{"name":"Binary Search"}],"frontendQuestionId":"704","paidOnly":False},
    {"titleSlug":"reverse-string","title":"Reverse String","difficulty":"Easy","acRate":75.4,"topicTags":[{"name":"String"},{"name":"Two Pointers"}],"frontendQuestionId":"344","paidOnly":False},
    {"titleSlug":"first-bad-version","title":"First Bad Version","difficulty":"Easy","acRate":43.2,"topicTags":[{"name":"Binary Search"}],"frontendQuestionId":"278","paidOnly":False},
    {"titleSlug":"ransom-note","title":"Ransom Note","difficulty":"Easy","acRate":57.8,"topicTags":[{"name":"Hash Table"},{"name":"String"}],"frontendQuestionId":"383","paidOnly":False},
    {"titleSlug":"longest-common-prefix","title":"Longest Common Prefix","difficulty":"Easy","acRate":40.7,"topicTags":[{"name":"String"},{"name":"Trie"}],"frontendQuestionId":"14","paidOnly":False},
    {"titleSlug":"add-two-numbers","title":"Add Two Numbers","difficulty":"Medium","acRate":40.7,"topicTags":[{"name":"Linked List"},{"name":"Math"}],"frontendQuestionId":"2","paidOnly":False},
    {"titleSlug":"longest-substring-without-repeating-characters","title":"Longest Substring Without Repeating Characters","difficulty":"Medium","acRate":33.8,"topicTags":[{"name":"Hash Table"},{"name":"Sliding Window"}],"frontendQuestionId":"3","paidOnly":False},
    {"titleSlug":"container-with-most-water","title":"Container With Most Water","difficulty":"Medium","acRate":54.0,"topicTags":[{"name":"Array"},{"name":"Greedy"}],"frontendQuestionId":"11","paidOnly":False},
    {"titleSlug":"3sum","title":"3Sum","difficulty":"Medium","acRate":32.0,"topicTags":[{"name":"Array"},{"name":"Two Pointers"}],"frontendQuestionId":"15","paidOnly":False},
    {"titleSlug":"letter-combinations-of-a-phone-number","title":"Letter Combinations of a Phone Number","difficulty":"Medium","acRate":57.8,"topicTags":[{"name":"Backtracking"},{"name":"Hash Table"}],"frontendQuestionId":"17","paidOnly":False},
    {"titleSlug":"generate-parentheses","title":"Generate Parentheses","difficulty":"Medium","acRate":72.6,"topicTags":[{"name":"Backtracking"},{"name":"String"}],"frontendQuestionId":"22","paidOnly":False},
    {"titleSlug":"search-in-rotated-sorted-array","title":"Search in Rotated Sorted Array","difficulty":"Medium","acRate":38.9,"topicTags":[{"name":"Array"},{"name":"Binary Search"}],"frontendQuestionId":"33","paidOnly":False},
    {"titleSlug":"find-first-and-last-position-of-element-in-sorted-array","title":"Find First and Last Position of Element in Sorted Array","difficulty":"Medium","acRate":42.0,"topicTags":[{"name":"Array"},{"name":"Binary Search"}],"frontendQuestionId":"34","paidOnly":False},
    {"titleSlug":"permutations","title":"Permutations","difficulty":"Medium","acRate":76.3,"topicTags":[{"name":"Backtracking"},{"name":"Array"}],"frontendQuestionId":"46","paidOnly":False},
    {"titleSlug":"rotate-image","title":"Rotate Image","difficulty":"Medium","acRate":72.4,"topicTags":[{"name":"Array"},{"name":"Math"}],"frontendQuestionId":"48","paidOnly":False},
    {"titleSlug":"group-anagrams","title":"Group Anagrams","difficulty":"Medium","acRate":66.8,"topicTags":[{"name":"Array"},{"name":"Hash Table"}],"frontendQuestionId":"49","paidOnly":False},
    {"titleSlug":"maximum-depth-of-binary-tree","title":"Maximum Depth of Binary Tree","difficulty":"Easy","acRate":73.8,"topicTags":[{"name":"Tree"},{"name":"DFS"}],"frontendQuestionId":"104","paidOnly":False},
    {"titleSlug":"coin-change","title":"Coin Change","difficulty":"Medium","acRate":41.5,"topicTags":[{"name":"Dynamic Programming"},{"name":"Array"}],"frontendQuestionId":"322","paidOnly":False},
    {"titleSlug":"number-of-islands","title":"Number of Islands","difficulty":"Medium","acRate":57.5,"topicTags":[{"name":"Graph"},{"name":"BFS"},{"name":"DFS"}],"frontendQuestionId":"200","paidOnly":False},
    {"titleSlug":"product-of-array-except-self","title":"Product of Array Except Self","difficulty":"Medium","acRate":64.4,"topicTags":[{"name":"Array"},{"name":"Prefix Sum"}],"frontendQuestionId":"238","paidOnly":False},
    {"titleSlug":"validate-binary-search-tree","title":"Validate Binary Search Tree","difficulty":"Medium","acRate":31.8,"topicTags":[{"name":"Tree"},{"name":"DFS"}],"frontendQuestionId":"98","paidOnly":False},
    {"titleSlug":"lru-cache","title":"LRU Cache","difficulty":"Medium","acRate":40.6,"topicTags":[{"name":"Hash Table"},{"name":"Linked List"},{"name":"Design"}],"frontendQuestionId":"146","paidOnly":False},
    {"titleSlug":"word-search","title":"Word Search","difficulty":"Medium","acRate":40.7,"topicTags":[{"name":"Backtracking"},{"name":"DFS"}],"frontendQuestionId":"79","paidOnly":False},
    {"titleSlug":"spiral-matrix","title":"Spiral Matrix","difficulty":"Medium","acRate":44.8,"topicTags":[{"name":"Array"},{"name":"Simulation"}],"frontendQuestionId":"54","paidOnly":False},
    {"titleSlug":"jump-game","title":"Jump Game","difficulty":"Medium","acRate":38.9,"topicTags":[{"name":"Array"},{"name":"Greedy"}],"frontendQuestionId":"55","paidOnly":False},
    {"titleSlug":"merge-intervals","title":"Merge Intervals","difficulty":"Medium","acRate":46.3,"topicTags":[{"name":"Array"},{"name":"Sorting"}],"frontendQuestionId":"56","paidOnly":False},
    {"titleSlug":"unique-paths","title":"Unique Paths","difficulty":"Medium","acRate":62.2,"topicTags":[{"name":"Dynamic Programming"},{"name":"Math"}],"frontendQuestionId":"62","paidOnly":False},
    {"titleSlug":"word-break","title":"Word Break","difficulty":"Medium","acRate":45.7,"topicTags":[{"name":"Dynamic Programming"},{"name":"Trie"}],"frontendQuestionId":"139","paidOnly":False},
    {"titleSlug":"course-schedule","title":"Course Schedule","difficulty":"Medium","acRate":46.0,"topicTags":[{"name":"Graph"},{"name":"Topological Sort"}],"frontendQuestionId":"207","paidOnly":False},
    {"titleSlug":"implement-trie-prefix-tree","title":"Implement Trie (Prefix Tree)","difficulty":"Medium","acRate":63.6,"topicTags":[{"name":"Trie"},{"name":"Design"}],"frontendQuestionId":"208","paidOnly":False},
    {"titleSlug":"median-of-two-sorted-arrays","title":"Median of Two Sorted Arrays","difficulty":"Hard","acRate":37.9,"topicTags":[{"name":"Array"},{"name":"Binary Search"}],"frontendQuestionId":"4","paidOnly":False},
    {"titleSlug":"trapping-rain-water","title":"Trapping Rain Water","difficulty":"Hard","acRate":60.7,"topicTags":[{"name":"Array"},{"name":"Two Pointers"},{"name":"Stack"}],"frontendQuestionId":"42","paidOnly":False},
    {"titleSlug":"merge-k-sorted-lists","title":"Merge K Sorted Lists","difficulty":"Hard","acRate":49.5,"topicTags":[{"name":"Linked List"},{"name":"Heap"}],"frontendQuestionId":"23","paidOnly":False},
    {"titleSlug":"word-ladder","title":"Word Ladder","difficulty":"Hard","acRate":37.6,"topicTags":[{"name":"Graph"},{"name":"BFS"}],"frontendQuestionId":"127","paidOnly":False},
    {"titleSlug":"regular-expression-matching","title":"Regular Expression Matching","difficulty":"Hard","acRate":28.2,"topicTags":[{"name":"Dynamic Programming"},{"name":"String"}],"frontendQuestionId":"10","paidOnly":False},
    {"titleSlug":"serialize-and-deserialize-binary-tree","title":"Serialize and Deserialize Binary Tree","difficulty":"Hard","acRate":55.0,"topicTags":[{"name":"Tree"},{"name":"DFS"},{"name":"BFS"}],"frontendQuestionId":"297","paidOnly":False},
    {"titleSlug":"find-median-from-data-stream","title":"Find Median from Data Stream","difficulty":"Hard","acRate":51.3,"topicTags":[{"name":"Heap"},{"name":"Design"}],"frontendQuestionId":"295","paidOnly":False},
    {"titleSlug":"sliding-window-maximum","title":"Sliding Window Maximum","difficulty":"Hard","acRate":46.5,"topicTags":[{"name":"Sliding Window"},{"name":"Heap"}],"frontendQuestionId":"239","paidOnly":False},
]

# ─────────────────────────────────────────────
#  API HELPERS
# ─────────────────────────────────────────────

async def lc_fetch_problems(limit=50, skip=0, difficulty=None, tags=None, search=None):
    filters = {}
    if difficulty: filters["difficulty"] = difficulty.upper()
    if tags:       filters["tags"] = tags
    if search:     filters["searchKeywords"] = search

    payload = {"query": PROBLEMS_QUERY, "variables": {
        "categorySlug": "", "limit": limit, "skip": skip, "filters": filters
    }}
    try:
        async with httpx.AsyncClient(timeout=12.0) as c:
            r = await c.post(LEETCODE_GRAPHQL, json=payload, headers=HEADERS)
            r.raise_for_status()
            return r.json().get("data", {}).get("problemsetQuestionList", {})
    except Exception as e:
        print(f"[LeetCode] problems fetch failed: {e}")
        return {}


async def lc_fetch_detail(slug: str):
    if slug in cache["problem_details"]:
        return cache["problem_details"][slug]
    payload = {"query": DETAIL_QUERY, "variables": {"titleSlug": slug}}
    try:
        async with httpx.AsyncClient(timeout=12.0) as c:
            r = await c.post(LEETCODE_GRAPHQL, json=payload, headers=HEADERS)
            r.raise_for_status()
            q = r.json().get("data", {}).get("question")
            if q:
                cache["problem_details"][slug] = q
            return q
    except Exception as e:
        print(f"[LeetCode] detail fetch failed: {e}")
        return None


async def lc_fetch_daily():
    if cache["daily"] and is_fresh("daily"):
        return cache["daily"]
    payload = {"query": DAILY_QUERY, "variables": {}}
    try:
        async with httpx.AsyncClient(timeout=12.0) as c:
            r = await c.post(LEETCODE_GRAPHQL, json=payload, headers=HEADERS)
            r.raise_for_status()
            d = r.json().get("data", {}).get("activeDailyCodingChallengeQuestion")
            if d:
                cache["daily"] = d
                cache["daily_time"] = datetime.utcnow()
            return d
    except Exception as e:
        print(f"[LeetCode] daily fetch failed: {e}")
        return None

# ─────────────────────────────────────────────
#  TRANSFORMERS
# ─────────────────────────────────────────────

TAG_TO_CATEGORY = {
    "Array": "Arrays", "String": "Strings", "Hash Table": "Hash Tables",
    "Dynamic Programming": "Dynamic Programming", "Tree": "Trees",
    "Graph": "Graphs", "Linked List": "Linked List", "Stack": "Stack",
    "Queue": "Queue", "Heap (Priority Queue)": "Heap", "Heap": "Heap",
    "Binary Search": "Binary Search", "Two Pointers": "Two Pointers",
    "Sliding Window": "Sliding Window", "Backtracking": "Backtracking",
    "Greedy": "Greedy", "Sorting": "Sorting", "Math": "Math",
    "Recursion": "Recursion", "Divide and Conquer": "Divide and Conquer",
    "BFS": "Graphs", "DFS": "Graphs", "Trie": "Trie", "Design": "Design",
}

def get_category(tags):
    for t in tags:
        if t in TAG_TO_CATEGORY:
            return TAG_TO_CATEGORY[t]
    return tags[0] if tags else "Algorithms"

def to_problem(q):
    tags = [t["name"] for t in q.get("topicTags", [])]
    slug = q.get("titleSlug", "")
    ac = q.get("acRate", 0)
    return {
        "id": slug, "title": q.get("title", ""), "slug": slug,
        "difficulty": q.get("difficulty", "Medium").lower(),
        "category": get_category(tags), "tags": tags[:5],
        "platformLink": f"https://leetcode.com/problems/{slug}/",
        "companies_asked": [],
        "frequency_score": round((q.get("freqBar") or 0) / 100, 2),
        "acceptance_rate": round(ac, 1) if ac else 0,
        "time_complexity": "", "space_complexity": "",
        "question_id": q.get("frontendQuestionId", ""),
        "paid_only": q.get("paidOnly", False),
        "source": "leetcode",
    }

def to_detail(q):
    content = q.get("content") or ""
    clean = re.sub(r'<[^>]+>', ' ', content)
    for ent, rep in [("&nbsp;"," "),("&lt;","<"),("&gt;",">"),("&amp;","&"),("&#39;","'"),("&quot;",'"')]:
        clean = clean.replace(ent, rep)
    clean = re.sub(r'\s+', ' ', clean).strip()

    tags = [t["name"] for t in q.get("topicTags", [])]
    slug = q.get("titleSlug", "")

    ac = 0
    try:
        stats = json.loads(q.get("stats") or "{}")
        ac = float(stats.get("acRate", "0").replace("%", ""))
    except Exception:
        pass

    examples = (q.get("exampleTestcases") or "").strip().split("\n")

    return {
        "id": slug, "title": q.get("title", ""), "slug": slug,
        "difficulty": q.get("difficulty", "Medium").lower(),
        "category": get_category(tags), "tags": tags,
        "description": clean[:4000],
        "constraints": [],
        "inputFormat": "See full description on LeetCode.",
        "outputFormat": "See full description on LeetCode.",
        "exampleInput": examples[0] if examples else "",
        "exampleOutput": examples[1] if len(examples) > 1 else "",
        "explanation": "",
        "platformLink": f"https://leetcode.com/problems/{slug}/",
        "companies_asked": [],
        "frequency_score": 0,
        "acceptance_rate": round(ac, 1),
        "time_complexity": "", "space_complexity": "",
        "hints": (q.get("hints") or [])[:3],
        "question_id": q.get("questionFrontendId", ""),
        "source": "leetcode",
    }

def sort_problems(problems, sort_by):
    if sort_by == "acceptance":
        return sorted(problems, key=lambda x: x.get("acceptance_rate", 0), reverse=True)
    if sort_by == "difficulty_asc":
        o = {"easy":0,"medium":1,"hard":2}
        return sorted(problems, key=lambda x: o.get(x["difficulty"],1))
    if sort_by == "difficulty_desc":
        o = {"easy":0,"medium":1,"hard":2}
        return sorted(problems, key=lambda x: o.get(x["difficulty"],1), reverse=True)
    if sort_by == "id_asc":
        return sorted(problems, key=lambda x: int(x.get("question_id") or 0))
    # default: frequency
    return sorted(problems, key=lambda x: x.get("frequency_score", 0), reverse=True)

# ─────────────────────────────────────────────
#  FASTAPI APP
# ─────────────────────────────────────────────

app = FastAPI(title="DSA Practice Service", version="3.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

TOPICS = [
    "Array", "String", "Hash Table", "Dynamic Programming", "Tree", "Graph",
    "Linked List", "Stack", "Queue", "Binary Search", "Two Pointers",
    "Sliding Window", "Backtracking", "Greedy", "Sorting", "Math",
    "Recursion", "Divide and Conquer", "Heap (Priority Queue)",
    "Bit Manipulation", "Depth-First Search", "Breadth-First Search",
    "Prefix Sum", "Design", "Trie",
]

@app.get("/api/problems")
async def list_problems(
    difficulty: Optional[str] = None,
    topic:      Optional[str] = None,
    search:     Optional[str] = None,
    sort_by:    str = Query("frequency", enum=["frequency","acceptance","difficulty_asc","difficulty_desc","id_asc"]),
    limit:      int = Query(20, ge=1, le=100),
    offset:     int = Query(0, ge=0),
):
    tags = [topic] if topic else None
    data = await lc_fetch_problems(limit=limit, skip=offset,
                                    difficulty=difficulty, tags=tags, search=search)
    questions = data.get("questions", [])
    total_api = data.get("total", 0)

    if questions:
        problems = [to_problem(q) for q in questions if not q.get("paidOnly")]
        using_fallback = False
    else:
        problems = [to_problem(q) for q in FALLBACK_PROBLEMS]
        using_fallback = True
        if difficulty:
            problems = [p for p in problems if p["difficulty"] == difficulty.lower()]
        if search:
            s = search.lower()
            problems = [p for p in problems if s in p["title"].lower() or any(s in t.lower() for t in p["tags"])]
        if topic:
            problems = [p for p in problems if topic in p["tags"]]

    problems = sort_problems(problems, sort_by)
    total = len(problems) if using_fallback else (total_api or len(problems))
    return {
        "problems": problems if not using_fallback else problems[offset:offset+limit],
        "total": total, "limit": limit, "offset": offset,
        "source": "fallback" if using_fallback else "leetcode",
    }


@app.get("/api/problems/{slug}")
async def get_problem(slug: str):
    q = await lc_fetch_detail(slug)
    if q:
        if q.get("isPaidOnly"):
            raise HTTPException(403, "Premium LeetCode problem — requires subscription.")
        return to_detail(q)

    fb = next((p for p in FALLBACK_PROBLEMS if p["titleSlug"] == slug), None)
    if fb:
        tags = [t["name"] for t in fb.get("topicTags", [])]
        return {
            "id": slug, "title": fb["title"], "slug": slug,
            "difficulty": fb["difficulty"].lower(),
            "category": get_category(tags), "tags": tags,
            "description": "Full description available on LeetCode. Click 'Solve →' to view.",
            "constraints": [], "inputFormat": "", "outputFormat": "",
            "exampleInput": "", "exampleOutput": "", "explanation": "",
            "platformLink": f"https://leetcode.com/problems/{slug}/",
            "companies_asked": [], "frequency_score": 0,
            "acceptance_rate": round(fb.get("acRate", 0), 1),
            "time_complexity": "", "space_complexity": "",
            "hints": [], "source": "fallback",
        }
    raise HTTPException(404, "Problem not found")


@app.get("/api/daily-problem")
async def daily_problem():
    d = await lc_fetch_daily()
    if d:
        q = d.get("question", {})
        tags = [t["name"] for t in q.get("topicTags", [])]
        slug = q.get("titleSlug", "")
        ac = q.get("acRate", 0)
        return {
            "id": slug, "title": q.get("title",""), "slug": slug,
            "difficulty": q.get("difficulty","Medium").lower(),
            "category": get_category(tags), "tags": tags,
            "platformLink": f"https://leetcode.com{d.get('link', f'/problems/{slug}/')}",
            "acceptance_rate": round(ac,1) if ac else 0,
            "time_complexity": "",
            "date": d.get("date", date.today().isoformat()),
            "source": "leetcode",
        }
    idx = (date.today() - date(date.today().year,1,1)).days % len(FALLBACK_PROBLEMS)
    p = FALLBACK_PROBLEMS[idx]
    tags = [t["name"] for t in p.get("topicTags",[])]
    return {
        "id": p["titleSlug"], "title": p["title"], "slug": p["titleSlug"],
        "difficulty": p["difficulty"].lower(), "category": get_category(tags), "tags": tags,
        "platformLink": f"https://leetcode.com/problems/{p['titleSlug']}/",
        "acceptance_rate": round(p.get("acRate",0),1),
        "time_complexity": "", "date": date.today().isoformat(), "source": "fallback",
    }


@app.get("/api/topics")
async def get_topics():
    return {"topics": TOPICS}


@app.get("/api/difficulties")
async def get_difficulties():
    easy   = await lc_fetch_problems(limit=1, difficulty="easy")
    medium = await lc_fetch_problems(limit=1, difficulty="medium")
    hard   = await lc_fetch_problems(limit=1, difficulty="hard")
    return {"difficulties": [
        {"value":"easy",   "label":"Easy",   "count": easy.get("total",0)   or sum(1 for p in FALLBACK_PROBLEMS if p["difficulty"]=="Easy")},
        {"value":"medium", "label":"Medium", "count": medium.get("total",0) or sum(1 for p in FALLBACK_PROBLEMS if p["difficulty"]=="Medium")},
        {"value":"hard",   "label":"Hard",   "count": hard.get("total",0)   or sum(1 for p in FALLBACK_PROBLEMS if p["difficulty"]=="Hard")},
    ]}


@app.get("/api/companies")
async def get_companies():
    return {"companies": sorted([
        "Google","Amazon","Meta","Microsoft","Apple","Netflix","Uber",
        "Airbnb","LinkedIn","Twitter","Bloomberg","Adobe","Salesforce",
        "Oracle","IBM","TikTok","ByteDance","Snap","Lyft","Stripe",
    ])}


@app.get("/api/stats")
async def get_stats():
    data = await lc_fetch_problems(limit=1)
    total = data.get("total", 0)
    easy_d   = await lc_fetch_problems(limit=1, difficulty="easy")
    medium_d = await lc_fetch_problems(limit=1, difficulty="medium")
    hard_d   = await lc_fetch_problems(limit=1, difficulty="hard")
    return {
        "total":     total or len(FALLBACK_PROBLEMS),
        "easy":      easy_d.get("total",0)   or 15,
        "medium":    medium_d.get("total",0) or 20,
        "hard":      hard_d.get("total",0)   or 13,
        "topics":    len(TOPICS),
        "companies": 20,
        "source":    "leetcode" if total else "fallback",
    }


@app.get("/health")
async def health():
    lc_ok = False
    try:
        async with httpx.AsyncClient(timeout=5.0) as c:
            r = await c.get("https://leetcode.com", headers=HEADERS)
            lc_ok = r.status_code < 500
    except Exception:
        lc_ok = False
    return {
        "status": "healthy", "service": "dsa-practice-v3",
        "leetcode_reachable": lc_ok,
        "cached_details": len(cache["problem_details"]),
        "fallback_count": len(FALLBACK_PROBLEMS),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)