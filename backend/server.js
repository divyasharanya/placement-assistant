const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const fs = require('fs');
const path = require('path');
const multer = require('multer');
const pdfParse = require('pdf-parse');
const mammoth = require('mammoth');
const http = require('http');
const { Server } = require('socket.io');

// Groq client for AI
const Groq = require('groq-sdk');

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST']
  }
});

const PORT = 8000;
const JWT_SECRET = 'your-secret-key-change-in-production';

// Initialize Groq client (will use GROQ_API_KEY env var)
let groq = null;
try {
  const GROQ_API_KEY = fs.readFileSync('D:\\placement_assisstant\\backend\\groq_key.txt', 'utf8').trim();
  groq = new Groq({ apiKey: GROQ_API_KEY });
} catch (e) {
  console.log('Groq client not initialized - set GROQ_API_KEY environment variable');
}

// Interview session storage (in-memory for demo, use Redis in production)
const interviewSessions = new Map();

// Interview questions bank
const questionBank = {
  dsa: [
    "Explain the difference between an array and a linked list. When would you use each?",
    "What is the time complexity of accessing an element in an array?",
    "Describe the binary search algorithm. What's its time complexity?",
    "What is a hash table? How does it handle collisions?",
    "Explain the concept of recursion with an example.",
    "What is the difference between DFS and BFS?",
    "Describe the bubble sort algorithm. What's its time complexity?",
    "What is a stack and queue? Give real-world examples of each.",
    "Explain the tree data structure and binary trees.",
    "What is dynamic programming? When is it useful?"
  ],
  oop: [
    "What are the four pillars of object-oriented programming?",
    "Explain the difference between inheritance and composition.",
    "What is polymorphism? Give an example.",
    "What is the difference between abstract class and interface?",
    "Explain the concept of encapsulation.",
    "What is a constructor? What's the difference between constructor and destructor?",
    "What are static methods and properties?",
    "Explain the difference between public, private, and protected.",
    "What is a singleton pattern? When would you use it?",
    "What is dependency injection?"
  ],
  system_design: [
    "Design a URL shortening service like bit.ly. What are the key components?",
    "How would you design a real-time chat application?",
    "Design a distributed cache system. How would you handle cache invalidation?",
    "What is load balancing? What algorithms do you know?",
    "Explain the concept of microservices architecture.",
    "How would you design a rate limiting system?",
    "What is CAP theorem? How does it affect system design?",
    "Design a notification system that can handle millions of users.",
    "How would you design a search autocomplete feature?",
    "What is database sharding? When would you use it?"
  ],
  behavioral: [
    "Tell me about yourself and your background.",
    "What is your greatest strength and weakness?",
    "Describe a challenging technical problem you solved. What was your approach?",
    "Tell me about a time you had a conflict with a teammate. How did you handle it?",
    "Why do you want to work at this company?",
    "Where do you see yourself in 5 years?",
    "Describe a project you're most proud of. What was the impact?",
    "How do you handle tight deadlines?",
    "Tell me about a time you failed. What did you learn from it?",
    "How do you keep up with new technologies?"
  ]
};

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Ensure uploads directory exists
const uploadsDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir);
}

// Multer config
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadsDir);
  },
  filename: (req, file, cb) => {
    cb(null, Date.now() + '-' + file.originalname);
  }
});
const upload = multer({ storage });

// Users file
const usersFilePath = path.join(__dirname, 'users.json');

function loadUsers() {
  try {
    if (fs.existsSync(usersFilePath)) {
      return JSON.parse(fs.readFileSync(usersFilePath, 'utf8'));
    }
  } catch (e) { console.error('Error loading users:', e); }
  return [];
}

function saveUsers(users) {
  fs.writeFileSync(usersFilePath, JSON.stringify(users, null, 2));
}

// ========== AUTH ROUTES ==========

// POST /api/register
app.post('/api/register', async (req, res) => {
  try {
    const { email, password, full_name } = req.body;
    
    if (!email || !password || !full_name) {
      return res.status(400).json({ error: 'All fields required' });
    }

    const users = loadUsers();
    if (users.find(u => u.email === email)) {
      return res.status(400).json({ error: 'Email already registered' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    const newUser = {
      id: Date.now().toString(),
      email,
      password_hash: hashedPassword,
      full_name,
      created_at: new Date().toISOString()
    };

    users.push(newUser);
    saveUsers(users);

    const token = jwt.sign({ user_id: newUser.id, email }, JWT_SECRET, { expiresIn: '30d' });

    res.status(201).json({
      access_token: token,
      token_type: 'bearer',
      user: { id: newUser.id, email, full_name }
    });
  } catch (error) {
    console.error('Register error:', error);
    res.status(500).json({ error: 'Registration failed' });
  }
});

// POST /api/login
app.post('/api/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    
    if (!email || !password) {
      return res.status(400).json({ error: 'Email and password required' });
    }

    const users = loadUsers();
    const user = users.find(u => u.email === email);
    
    // Handle both password and password_hash for backwards compatibility
    const storedHash = user?.password_hash || user?.password;
    
    if (!user || !storedHash || !await bcrypt.compare(password, storedHash)) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const token = jwt.sign({ user_id: user.id, email }, JWT_SECRET, { expiresIn: '30d' });

    res.json({
      access_token: token,
      token_type: 'bearer',
      user: { id: user.id, email, full_name: user.full_name }
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: 'Login failed' });
  }
});

// GET /api/me
app.get('/api/me', (req, res) => {
  try {
    const auth = req.headers.authorization;
    if (!auth?.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'No token' });
    }
    
    const token = auth.split(' ')[1];
    const decoded = jwt.verify(token, JWT_SECRET);
    const users = loadUsers();
    const user = users.find(u => u.id === decoded.user_id);
    
    if (!user) return res.status(401).json({ error: 'User not found' });
    
    res.json({ id: user.id, email: user.email, full_name: user.full_name });
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' });
  }
});

// ========== RESUME ANALYSIS ==========

// POST /api/analyze-resume
app.post('/api/analyze-resume', upload.single('resume'), async (req, res) => {
  try {
    console.log('Resume upload received:', req.file);
    
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    let text = '';
    const filePath = req.file.path;

    try {
      if (req.file.mimetype === 'application/pdf') {
        const dataBuffer = fs.readFileSync(filePath);
        const pdfData = await pdfParse(dataBuffer);
        text = pdfData.text;
      } else if (req.file.mimetype.includes('word') || req.file.originalname.endsWith('.docx')) {
        const result = await mammoth.extractRawText({ path: filePath });
        text = result.value;
      } else {
        text = fs.readFileSync(filePath, 'utf8');
      }
    } catch (parseError) {
      console.error('Parse error:', parseError);
      text = 'Could not extract text from file';
    }

    // Clean up
    try { fs.unlinkSync(filePath); } catch (e) {}

    // AI Analysis (mock - replace with real AI)
    const analysis = {
      score: Math.floor(Math.random() * 20) + 75,
      overall_feedback: 'Your resume shows good technical skills but could use more quantifiable achievements.',
      strengths: [
        'Strong technical skill section',
        'Clear education background',
        'Relevant project experience'
      ],
      improvements: [
        'Add metrics to your achievements (e.g., "Improved performance by 40%")',
        'Include more keywords from job descriptions',
        'Add a brief professional summary at the top'
      ],
      keywords_found: ['JavaScript', 'React', 'Node.js', 'Python'],
      missing_keywords: ['Docker', 'AWS', 'CI/CD', 'TypeScript'],
      formatting_score: 85,
      content_score: 78,
      ats_compatible: true
    };

    res.json({
      success: true,
      analysis,
      filename: req.file.originalname,
      text_preview: text.substring(0, 1000)
    });
    
  } catch (error) {
    console.error('Resume analysis error:', error);
    res.status(500).json({ error: 'Failed to analyze resume: ' + error.message });
  }
});

// ========== PRACTICE CODING ==========

// GET /api/practice-problems
app.get('/api/practice-problems', (req, res) => {
  const problems = [
    {
      id: 1,
      title: 'Two Sum',
      difficulty: 'Easy',
      category: 'Arrays',
      platform: 'LeetCode',
      description: 'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.',
      examples: [
        { input: 'nums = [2,7,11,15], target = 9', output: '[0,1]', explanation: 'Because nums[0] + nums[1] == 9, we return [0, 1].' }
      ],
      constraints: ['2 <= nums.length <= 10^4', '-10^9 <= nums[i] <= 10^9', '-10^9 <= target <= 10^9'],
      starter_code: {
        javascript: '/**\n * @param {number[]} nums\n * @param {number} target\n * @return {number[]}\n */\nfunction twoSum(nums, target) {\n    // Write your code here\n    \n};',
        python: 'def twoSum(nums, target):\n    """\n    :type nums: List[int]\n    :type target: int\n    :rtype: List[int]\n    """\n    # Write your code here\n    pass',
        java: 'class Solution {\n    public int[] twoSum(int[] nums, int target) {\n        // Write your code here\n        \n    }\n}'
      },
      url: 'https://leetcode.com/problems/two-sum/'
    },
    {
      id: 2,
      title: 'Valid Parentheses',
      difficulty: 'Easy',
      category: 'Stack',
      platform: 'LeetCode',
      description: 'Given a string s containing just the characters "(", ")", "{", "}", "[" and "]", determine if the input string is valid.',
      examples: [
        { input: 's = "()"', output: 'true' },
        { input: 's = "()[]{}"', output: 'true' },
        { input: 's = "(]"', output: 'false' }
      ],
      constraints: ['1 <= s.length <= 10^4', 's consists of parentheses only "()[]{}"'],
      starter_code: {
        javascript: '/**\n * @param {string} s\n * @return {boolean}\n */\nfunction isValid(s) {\n    // Write your code here\n    \n};',
        python: 'def isValid(s):\n    """\n    :type s: str\n    :rtype: bool\n    """\n    # Write your code here\n    pass'
      },
      url: 'https://leetcode.com/problems/valid-parentheses/'
    },
    {
      id: 3,
      title: 'Merge Two Sorted Lists',
      difficulty: 'Easy',
      category: 'Linked List',
      platform: 'LeetCode',
      description: 'You are given the heads of two sorted linked lists list1 and list2. Merge the two lists into one sorted list.',
      examples: [
        { input: 'list1 = [1,2,4], list2 = [1,3,4]', output: '[1,1,2,3,4,4]' }
      ],
      constraints: ['The number of nodes in both lists is in the range [0, 50]', '-100 <= Node.val <= 100'],
      starter_code: {
        javascript: '/**\n * Definition for singly-linked list.\n * function ListNode(val, next) {\n *     this.val = (val===undefined ? 0 : val)\n *     this.next = (next===undefined ? null : next)\n * }\n */\n/**\n * @param {ListNode} list1\n * @param {ListNode} list2\n * @return {ListNode}\n */\nfunction mergeTwoLists(list1, list2) {\n    // Write your code here\n    \n};',
        python: '# Definition for singly-linked list.\n# class ListNode:\n#     def __init__(self, val=0, next=None):\n#         self.val = val\n#         self.next = next\n\ndef mergeTwoLists(list1, list2):\n    """\n    :type list1: Optional[ListNode]\n    :type list2: Optional[ListNode]\n    :rtype: Optional[ListNode]\n    """\n    # Write your code here\n    pass'
      },
      url: 'https://leetcode.com/problems/merge-two-sorted-lists/'
    },
    {
      id: 4,
      title: 'Best Time to Buy and Sell Stock',
      difficulty: 'Easy',
      category: 'Dynamic Programming',
      platform: 'LeetCode',
      description: 'You are given an array prices where prices[i] is the price of a given stock on the ith day. Maximize profit by choosing a single day to buy and a different day to sell.',
      examples: [
        { input: 'prices = [7,1,5,3,6,4]', output: '5', explanation: 'Buy on day 2 (price = 1) and sell on day 5 (price = 6), profit = 6-1 = 5.' }
      ],
      starter_code: {
        javascript: '/**\n * @param {number[]} prices\n * @return {number}\n */\nfunction maxProfit(prices) {\n    // Write your code here\n    \n};',
        python: 'def maxProfit(prices):\n    """\n    :type prices: List[int]\n    :rtype: int\n    """\n    # Write your code here\n    pass'
      },
      url: 'https://leetcode.com/problems/best-time-to-buy-and-sell-stock/'
    },
    {
      id: 5,
      title: 'Valid Anagram',
      difficulty: 'Easy',
      category: 'Hash Table',
      platform: 'LeetCode',
      description: 'Given two strings s and t, return true if t is an anagram of s, and false otherwise.',
      examples: [
        { input: 's = "anagram", t = "nagaram"', output: 'true' },
        { input: 's = "rat", t = "car"', output: 'false' }
      ],
      starter_code: {
        javascript: '/**\n * @param {string} s\n * @param {string} t\n * @return {boolean}\n */\nfunction isAnagram(s, t) {\n    // Write your code here\n    \n};',
        python: 'def isAnagram(s, t):\n    """\n    :type s: str\n    :type t: str\n    :rtype: bool\n    """\n    # Write your code here\n    pass'
      },
      url: 'https://leetcode.com/problems/valid-anagram/'
    },
    {
      id: 6,
      title: 'Binary Tree Inorder Traversal',
      difficulty: 'Easy',
      category: 'Tree',
      platform: 'LeetCode',
      description: 'Given the root of a binary tree, return the inorder traversal of its nodes values.',
      examples: [
        { input: 'root = [1,null,2,3]', output: '[1,3,2]' }
      ],
      starter_code: {
        javascript: '/**\n * Definition for a binary tree node.\n * function TreeNode(val, left, right) {\n *     this.val = (val===undefined ? 0 : val)\n *     this.left = (left===undefined ? null : left)\n *     this.right = (right===undefined ? null : right)\n * }\n */\n/**\n * @param {TreeNode} root\n * @return {number[]}\n */\nfunction inorderTraversal(root) {\n    // Write your code here\n    \n};',
        python: '# Definition for a binary tree node.\n# class TreeNode:\n#     def __init__(self, val=0, left=None, right=None):\n#         self.val = val\n#         self.left = left\n#         self.right = right\n\ndef inorderTraversal(root):\n    """\n    :type root: Optional[TreeNode]\n    :rtype: List[int]\n    """\n    # Write your code here\n    pass'
      },
      url: 'https://leetcode.com/problems/binary-tree-inorder-traversal/'
    }
  ];

  res.json({ problems, total: problems.length });
});

// GET /api/daily-problem
// Returns a problem that changes based on the current date
app.get('/api/daily-problem', (req, res) => {
  const problems = [
    {
      id: 1,
      title: 'Two Sum',
      difficulty: 'Easy',
      category: 'Arrays',
      platform: 'LeetCode',
      description: 'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.',
      examples: [
        { input: 'nums = [2,7,11,15], target = 9', output: '[0,1]', explanation: 'Because nums[0] + nums[1] == 9, we return [0, 1].' }
      ],
      constraints: ['2 <= nums.length <= 10^4', '-10^9 <= nums[i] <= 10^9', '-10^9 <= target <= 10^9'],
      url: 'https://leetcode.com/problems/two-sum/'
    },
    {
      id: 2,
      title: 'Valid Parentheses',
      difficulty: 'Easy',
      category: 'Stack',
      platform: 'LeetCode',
      description: 'Given a string s containing just the characters "(", ")", "{", "}", "[" and "]", determine if the input string is valid.',
      examples: [
        { input: 's = "()"', output: 'true' },
        { input: 's = "()[]{}"', output: 'true' },
        { input: 's = "(]"', output: 'false' }
      ],
      constraints: ['1 <= s.length <= 10^4', 's consists of parentheses only "()[]{}"'],
      url: 'https://leetcode.com/problems/valid-parentheses/'
    },
    {
      id: 3,
      title: 'Merge Two Sorted Lists',
      difficulty: 'Easy',
      category: 'Linked List',
      platform: 'LeetCode',
      description: 'You are given the heads of two sorted linked lists list1 and list2. Merge the two lists into one sorted list.',
      examples: [
        { input: 'list1 = [1,2,4], list2 = [1,3,4]', output: '[1,1,2,3,4,4]' }
      ],
      constraints: ['The number of nodes in both lists is in the range [0, 50]', '-100 <= Node.val <= 100'],
      url: 'https://leetcode.com/problems/merge-two-sorted-lists/'
    },
    {
      id: 4,
      title: 'Best Time to Buy and Sell Stock',
      difficulty: 'Easy',
      category: 'Dynamic Programming',
      platform: 'LeetCode',
      description: 'You are given an array prices where prices[i] is the price of a given stock on the ith day. Maximize profit by choosing a single day to buy and a different day to sell.',
      examples: [
        { input: 'prices = [7,1,5,3,6,4]', output: '5', explanation: 'Buy on day 2 (price = 1) and sell on day 5 (price = 6), profit = 6-1 = 5.' }
      ],
      constraints: ['1 <= prices.length <= 10^5', '0 <= prices[i] <= 10^4'],
      url: 'https://leetcode.com/problems/best-time-to-buy-and-sell-stock/'
    },
    {
      id: 5,
      title: 'Valid Anagram',
      difficulty: 'Easy',
      category: 'Hash Table',
      platform: 'LeetCode',
      description: 'Given two strings s and t, return true if t is an anagram of s, and false otherwise.',
      examples: [
        { input: 's = "anagram", t = "nagaram"', output: 'true' },
        { input: 's = "rat", t = "car"', output: 'false' }
      ],
      constraints: ['1 <= s.length, t.length <= 5 * 10^4', 's and t consist of lowercase English letters.'],
      url: 'https://leetcode.com/problems/valid-anagram/'
    },
    {
      id: 6,
      title: 'Binary Tree Inorder Traversal',
      difficulty: 'Easy',
      category: 'Tree',
      platform: 'LeetCode',
      description: 'Given the root of a binary tree, return the inorder traversal of its nodes values.',
      examples: [
        { input: 'root = [1,null,2,3]', output: '[1,3,2]' }
      ],
      constraints: ['The number of nodes in the tree is in the range [0, 100]', '-100 <= Node.val <= 100'],
      url: 'https://leetcode.com/problems/binary-tree-inorder-traversal/'
    }
  ];
  
  // Use current date to select a problem - changes every day
  const today = new Date();
  const dayOfYear = Math.floor((today - new Date(today.getFullYear(), 0, 0)) / (1000 * 60 * 60 * 24));
  const problemIndex = dayOfYear % problems.length;
  const dailyProblem = problems[problemIndex];
  
  res.json({
    problem: dailyProblem,
    date: today.toISOString().split('T')[0]
  });
});

// GET /api/problems
// Returns all problems with optional filters
app.get('/api/problems', (req, res) => {
  const { difficulty, topic, search, limit = 20, offset = 0 } = req.query;
  
  const allProblems = [
    {
      id: '1',
      title: 'Two Sum',
      slug: 'two-sum',
      difficulty: 'Easy',
      category: 'Arrays',
      tags: ['Array', 'Hash Table'],
      platform: 'LeetCode',
      description: 'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.',
      examples: [
        { input: 'nums = [2,7,11,15], target = 9', output: '[0,1]', explanation: 'Because nums[0] + nums[1] == 9, we return [0, 1].' }
      ],
      constraints: ['2 <= nums.length <= 10^4', '-10^9 <= nums[i] <= 10^9', '-10^9 <= target <= 10^9'],
      inputFormat: 'First line contains n (number of elements). Second line contains n integers. Third line contains target integer.',
      outputFormat: 'Print two indices (0-based) separated by space.',
      platformLink: 'https://leetcode.com/problems/two-sum/',
      companies_asked: ['Google', 'Amazon', 'Apple', 'Microsoft', 'Facebook']
    },
    {
      id: '2',
      title: 'Valid Parentheses',
      slug: 'valid-parentheses',
      difficulty: 'Easy',
      category: 'Stack',
      tags: ['String', 'Stack'],
      platform: 'LeetCode',
      description: 'Given a string s containing just the characters "(", ")", "{", "}", "[" and "]", determine if the input string is valid.',
      examples: [
        { input: 's = "()"', output: 'true' },
        { input: 's = "()[]{}"', output: 'true' },
        { input: 's = "(]"', output: 'false' }
      ],
      constraints: ['1 <= s.length <= 10^4', 's consists of parentheses only "()[]{}"'],
      inputFormat: 'A string containing only parentheses characters.',
      outputFormat: 'Print true or false.',
      platformLink: 'https://leetcode.com/problems/valid-parentheses/',
      companies_asked: ['Amazon', 'Google', 'Bloomberg']
    },
    {
      id: '3',
      title: 'Merge Two Sorted Lists',
      slug: 'merge-two-sorted-lists',
      difficulty: 'Easy',
      category: 'Linked List',
      tags: ['Linked List', 'Recursion'],
      platform: 'LeetCode',
      description: 'You are given the heads of two sorted linked lists list1 and list2. Merge the two lists into one sorted list.',
      examples: [
        { input: 'list1 = [1,2,4], list2 = [1,3,4]', output: '[1,1,2,3,4,4]' }
      ],
      constraints: ['The number of nodes in both lists is in the range [0, 50]', '-100 <= Node.val <= 100'],
      inputFormat: 'Two sorted linked lists (given as arrays).',
      outputFormat: 'Merged sorted linked list as array.',
      platformLink: 'https://leetcode.com/problems/merge-two-sorted-lists/',
      companies_asked: ['Amazon', 'Apple', 'Microsoft']
    },
    {
      id: '4',
      title: 'Best Time to Buy and Sell Stock',
      slug: 'best-time-to-buy-and-sell-stock',
      difficulty: 'Easy',
      category: 'Dynamic Programming',
      tags: ['Array', 'Dynamic Programming'],
      platform: 'LeetCode',
      description: 'You are given an array prices where prices[i] is the price of a given stock on the ith day. Maximize profit by choosing a single day to buy and a different day to sell.',
      examples: [
        { input: 'prices = [7,1,5,3,6,4]', output: '5', explanation: 'Buy on day 2 (price = 1) and sell on day 5 (price = 6), profit = 6-1 = 5.' }
      ],
      constraints: ['1 <= prices.length <= 10^5', '0 <= prices[i] <= 10^4'],
      inputFormat: 'An array of stock prices.',
      outputFormat: 'Maximum profit possible.',
      platformLink: 'https://leetcode.com/problems/best-time-to-buy-and-sell-stock/',
      companies_asked: ['Amazon', 'Facebook', 'Microsoft', 'Google']
    },
    {
      id: '5',
      title: 'Valid Anagram',
      slug: 'valid-anagram',
      difficulty: 'Easy',
      category: 'Hash Table',
      tags: ['Hash Table', 'String', 'Sorting'],
      platform: 'LeetCode',
      description: 'Given two strings s and t, return true if t is an anagram of s, and false otherwise.',
      examples: [
        { input: 's = "anagram", t = "nagaram"', output: 'true' },
        { input: 's = "rat", t = "car"', output: 'false' }
      ],
      constraints: ['1 <= s.length, t.length <= 5 * 10^4', 's and t consist of lowercase English letters.'],
      inputFormat: 'Two strings s and t.',
      outputFormat: 'Print true or false.',
      platformLink: 'https://leetcode.com/problems/valid-anagram/',
      companies_asked: ['Google', 'Amazon', 'Facebook']
    },
    {
      id: '6',
      title: 'Binary Tree Inorder Traversal',
      slug: 'binary-tree-inorder-traversal',
      difficulty: 'Easy',
      category: 'Tree',
      tags: ['Tree', 'Stack', 'Depth-First Search'],
      platform: 'LeetCode',
      description: 'Given the root of a binary tree, return the inorder traversal of its nodes values.',
      examples: [
        { input: 'root = [1,null,2,3]', output: '[1,3,2]' }
      ],
      constraints: ['The number of nodes in the tree is in the range [0, 100]', '-100 <= Node.val <= 100'],
      inputFormat: 'Binary tree represented as array (level order).',
      outputFormat: 'Inorder traversal as array.',
      platformLink: 'https://leetcode.com/problems/binary-tree-inorder-traversal/',
      companies_asked: ['Microsoft', 'Amazon']
    },
    {
      id: '7',
      title: 'Maximum Subarray',
      slug: 'maximum-subarray',
      difficulty: 'Medium',
      category: 'Dynamic Programming',
      tags: ['Array', 'Divide and Conquer', 'Dynamic Programming'],
      platform: 'LeetCode',
      description: 'Given an integer array nums, find the subarray with the largest sum, and return its sum.',
      examples: [
        { input: 'nums = [-2,1,-3,4,-1,2,1,-5,4]', output: '6', explanation: 'The subarray [4,-1,2,1] has the largest sum 6.' }
      ],
      constraints: ['1 <= nums.length <= 10^5', '-10^4 <= nums[i] <= 10^4'],
      inputFormat: 'An array of integers.',
      outputFormat: 'Maximum sum of any non-empty subarray.',
      platformLink: 'https://leetcode.com/problems/maximum-subarray/',
      companies_asked: ['Amazon', 'Microsoft', 'Apple', 'LinkedIn']
    },
    {
      id: '8',
      title: 'Number of Islands',
      slug: 'number-of-islands',
      difficulty: 'Medium',
      category: 'Graphs',
      tags: ['Array', 'Depth-First Search', 'Breadth-First Search', 'Union Find', 'Matrix'],
      platform: 'LeetCode',
      description: 'Given an m x n 2D binary grid which represents a map of "1"s (land) and "0"s (water), return the number of islands.',
      examples: [
        { input: 'grid = [["1","1","1"],["0","1","0"],["1","1","1"]]', output: '1' }
      ],
      constraints: ['m == grid.length', 'n == grid[i].length', '1 <= m, n <= 300', 'grid[i][j] is "0" or "1"'],
      inputFormat: '2D grid of 0s and 1s.',
      outputFormat: 'Number of islands.',
      platformLink: 'https://leetcode.com/problems/number-of-islands/',
      companies_asked: ['Amazon', 'Facebook', 'Microsoft', 'Bloomberg']
    },
    {
      id: '9',
      title: 'Longest Palindromic Substring',
      slug: 'longest-palindromic-substring',
      difficulty: 'Medium',
      category: 'Strings',
      tags: ['String', 'Dynamic Programming'],
      platform: 'LeetCode',
      description: 'Given a string s, return the longest palindromic substring in s.',
      examples: [
        { input: 's = "babad"', output: '"bab"', explanation: '"aba" is also a valid answer.' },
        { input: 's = "cbbd"', output: '"bb"' }
      ],
      constraints: ['1 <= s.length <= 1000', 's consist of only digits and English letters.'],
      inputFormat: 'A string s.',
      outputFormat: 'Longest palindromic substring.',
      platformLink: 'https://leetcode.com/problems/longest-palindromic-substring/',
      companies_asked: ['Amazon', 'Google', 'Microsoft', 'Facebook']
    },
    {
      id: '10',
      title: 'Container With Most Water',
      slug: 'container-with-most-water',
      difficulty: 'Medium',
      category: 'Two Pointers',
      tags: ['Array', 'Two Pointers', 'Greedy'],
      platform: 'LeetCode',
      description: 'Given n non-negative integers height where each represents a point at coordinate (i, height[i]), find two lines that together with the x-axis form a container that contains the most water.',
      examples: [
        { input: 'height = [1,8,6,2,5,4,8,3,7]', output: '49', explanation: 'The max area is between height[1] and height[8].' }
      ],
      constraints: ['n == height.length', '2 <= n <= 10^5', '0 <= height[i] <= 10^4'],
      inputFormat: 'Array of integers representing heights.',
      outputFormat: 'Maximum area (water).',
      platformLink: 'https://leetcode.com/problems/container-with-most-water/',
      companies_asked: ['Amazon', 'Google', 'Microsoft', 'Facebook']
    },
    {
      id: '11',
      title: 'Word Search',
      slug: 'word-search',
      difficulty: 'Hard',
      category: 'Graphs',
      tags: ['Array', 'Backtracking', 'Depth-First Search', 'Breadth-First Search', 'Matrix'],
      platform: 'LeetCode',
      description: 'Given an m x n grid of characters board and a string word, return true if word exists in the grid.',
      examples: [
        { input: 'board = [["A","B"],["C","D"]], word = "ABCD"', output: 'false', explanation: 'Cannot find ABCD in the grid.' }
      ],
      constraints: ['m == board.length', 'n = board[i].length', '1 <= m, n <= 6', '1 <= word.length <= 15'],
      inputFormat: '2D grid of characters and a word to search.',
      outputFormat: 'true if word exists, false otherwise.',
      platformLink: 'https://leetcode.com/problems/word-search/',
      companies_asked: ['Facebook', 'Microsoft', 'Apple', 'LinkedIn']
    },
    {
      id: '12',
      title: 'Merge K Sorted Lists',
      slug: 'merge-k-sorted-lists',
      difficulty: 'Hard',
      category: 'Linked List',
      tags: ['Linked List', 'Divide and Conquer', 'Heap', 'Priority Queue'],
      platform: 'LeetCode',
      description: 'You are given an array of k linked-lists lists, each linked-list is sorted in ascending order. Merge all the linked-lists into one sorted linked-list and return it.',
      examples: [
        { input: 'lists = [[1,4,5],[1,3,4],[2,6]]', output: '[1,1,2,3,4,4,5,6]' }
      ],
      constraints: ['k == lists.length', '0 <= k <= 10^4', '0 <= lists[i].length <= 500'],
      inputFormat: 'Array of k sorted linked lists.',
      outputFormat: 'One merged sorted linked list.',
      platformLink: 'https://leetcode.com/problems/merge-k-sorted-lists/',
      companies_asked: ['Amazon', 'Google', 'Microsoft', 'Facebook']
    }
  ];
  
  let filtered = [...allProblems];
  
  // Apply filters
  if (difficulty && difficulty !== 'All') {
    filtered = filtered.filter(p => p.difficulty === difficulty);
  }
  
  if (topic && topic !== 'All') {
    filtered = filtered.filter(p => p.category === topic || p.tags.includes(topic));
  }
  
  if (search) {
    const searchLower = search.toLowerCase();
    filtered = filtered.filter(p => 
      p.title.toLowerCase().includes(searchLower) ||
      p.description.toLowerCase().includes(searchLower) ||
      p.tags.some(tag => tag.toLowerCase().includes(searchLower))
    );
  }
  
  const total = filtered.length;
  const paginated = filtered.slice(Number(offset), Number(offset) + Number(limit));
  
  res.json({ problems: paginated, total });
});

// GET /api/problems/:id
// Returns a single problem by ID
app.get('/api/problems/:id', (req, res) => {
  const { id } = req.params;
  
  const allProblems = [
    {
      id: '1',
      title: 'Two Sum',
      slug: 'two-sum',
      difficulty: 'Easy',
      category: 'Arrays',
      tags: ['Array', 'Hash Table'],
      platform: 'LeetCode',
      description: 'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. You may assume that each input would have exactly one solution, and you may not use the same element twice.',
      examples: [
        { input: 'nums = [2,7,11,15], target = 9', output: '[0,1]', explanation: 'Because nums[0] + nums[1] == 9, we return [0, 1].' }
      ],
      constraints: ['2 <= nums.length <= 10^4', '-10^9 <= nums[i] <= 10^9', '-10^9 <= target <= 10^9'],
      inputFormat: 'First line contains n (number of elements). Second line contains n integers. Third line contains target integer.',
      outputFormat: 'Print two indices (0-based) separated by space.',
      platformLink: 'https://leetcode.com/problems/two-sum/',
      companies_asked: ['Google', 'Amazon', 'Apple', 'Microsoft', 'Facebook']
    },
    {
      id: '2',
      title: 'Valid Parentheses',
      slug: 'valid-parentheses',
      difficulty: 'Easy',
      category: 'Stack',
      tags: ['String', 'Stack'],
      platform: 'LeetCode',
      description: 'Given a string s containing just the characters "(", ")", "{", "}", "[" and "]", determine if the input string is valid. An input string is valid if: Open brackets must be closed by the same type of brackets, and open brackets must be closed in the correct order.',
      examples: [
        { input: 's = "()"', output: 'true' },
        { input: 's = "()[]{}"', output: 'true' },
        { input: 's = "(]"', output: 'false' }
      ],
      constraints: ['1 <= s.length <= 10^4', 's consists of parentheses only "()[]{}"'],
      inputFormat: 'A string containing only parentheses characters.',
      outputFormat: 'Print true or false.',
      platformLink: 'https://leetcode.com/problems/valid-parentheses/',
      companies_asked: ['Amazon', 'Google', 'Bloomberg']
    },
    {
      id: '3',
      title: 'Merge Two Sorted Lists',
      slug: 'merge-two-sorted-lists',
      difficulty: 'Easy',
      category: 'Linked List',
      tags: ['Linked List', 'Recursion'],
      platform: 'LeetCode',
      description: 'You are given the heads of two sorted linked lists list1 and list2. Merge the two lists into one sorted list. The list should be made by splicing together the nodes of the first two lists.',
      examples: [
        { input: 'list1 = [1,2,4], list2 = [1,3,4]', output: '[1,1,2,3,4,4]' }
      ],
      constraints: ['The number of nodes in both lists is in the range [0, 50]', '-100 <= Node.val <= 100'],
      inputFormat: 'Two sorted linked lists (given as arrays).',
      outputFormat: 'Merged sorted linked list as array.',
      platformLink: 'https://leetcode.com/problems/merge-two-sorted-lists/',
      companies_asked: ['Amazon', 'Apple', 'Microsoft']
    },
    {
      id: '4',
      title: 'Best Time to Buy and Sell Stock',
      slug: 'best-time-to-buy-and-sell-stock',
      difficulty: 'Easy',
      category: 'Dynamic Programming',
      tags: ['Array', 'Dynamic Programming'],
      platform: 'LeetCode',
      description: 'You are given an array prices where prices[i] is the price of a given stock on the ith day. Maximize profit by choosing a single day to buy and a different day to sell. Return the maximum profit you can achieve from this transaction.',
      examples: [
        { input: 'prices = [7,1,5,3,6,4]', output: '5', explanation: 'Buy on day 2 (price = 1) and sell on day 5 (price = 6), profit = 6-1 = 5.' }
      ],
      constraints: ['1 <= prices.length <= 10^5', '0 <= prices[i] <= 10^4'],
      inputFormat: 'An array of stock prices.',
      outputFormat: 'Maximum profit possible.',
      platformLink: 'https://leetcode.com/problems/best-time-to-buy-and-sell-stock/',
      companies_asked: ['Amazon', 'Facebook', 'Microsoft', 'Google']
    },
    {
      id: '5',
      title: 'Valid Anagram',
      slug: 'valid-anagram',
      difficulty: 'Easy',
      category: 'Hash Table',
      tags: ['Hash Table', 'String', 'Sorting'],
      platform: 'LeetCode',
      description: 'Given two strings s and t, return true if t is an anagram of s, and false otherwise. An Anagram is a word or phrase formed by rearranging the letters of a different word or phrase, typically using all the original letters exactly once.',
      examples: [
        { input: 's = "anagram", t = "nagaram"', output: 'true' },
        { input: 's = "rat", t = "car"', output: 'false' }
      ],
      constraints: ['1 <= s.length, t.length <= 5 * 10^4', 's and t consist of lowercase English letters.'],
      inputFormat: 'Two strings s and t.',
      outputFormat: 'Print true or false.',
      platformLink: 'https://leetcode.com/problems/valid-anagram/',
      companies_asked: ['Google', 'Amazon', 'Facebook']
    },
    {
      id: '6',
      title: 'Binary Tree Inorder Traversal',
      slug: 'binary-tree-inorder-traversal',
      difficulty: 'Easy',
      category: 'Tree',
      tags: ['Tree', 'Stack', 'Depth-First Search'],
      platform: 'LeetCode',
      description: 'Given the root of a binary tree, return the inorder traversal of its nodes values. Inorder traversal visits nodes in the order: left, root, right.',
      examples: [
        { input: 'root = [1,null,2,3]', output: '[1,3,2]' }
      ],
      constraints: ['The number of nodes in the tree is in the range [0, 100]', '-100 <= Node.val <= 100'],
      inputFormat: 'Binary tree represented as array (level order).',
      outputFormat: 'Inorder traversal as array.',
      platformLink: 'https://leetcode.com/problems/binary-tree-inorder-traversal/',
      companies_asked: ['Microsoft', 'Amazon']
    },
    {
      id: '7',
      title: 'Maximum Subarray',
      slug: 'maximum-subarray',
      difficulty: 'Medium',
      category: 'Dynamic Programming',
      tags: ['Array', 'Divide and Conquer', 'Dynamic Programming'],
      platform: 'LeetCode',
      description: 'Given an integer array nums, find the subarray with the largest sum, and return its sum.',
      examples: [
        { input: 'nums = [-2,1,-3,4,-1,2,1,-5,4]', output: '6', explanation: 'The subarray [4,-1,2,1] has the largest sum 6.' }
      ],
      constraints: ['1 <= nums.length <= 10^5', '-10^4 <= nums[i] <= 10^4'],
      inputFormat: 'An array of integers.',
      outputFormat: 'Maximum sum of any non-empty subarray.',
      platformLink: 'https://leetcode.com/problems/maximum-subarray/',
      companies_asked: ['Amazon', 'Microsoft', 'Apple', 'LinkedIn']
    },
    {
      id: '8',
      title: 'Number of Islands',
      slug: 'number-of-islands',
      difficulty: 'Medium',
      category: 'Graphs',
      tags: ['Array', 'Depth-First Search', 'Breadth-First Search', 'Union Find', 'Matrix'],
      platform: 'LeetCode',
      description: 'Given an m x n 2D binary grid which represents a map of "1"s (land) and "0"s (water), return the number of islands. An island is surrounded by water and is formed by connecting adjacent lands horizontally or vertically.',
      examples: [
        { input: 'grid = [["1","1","1"],["0","1","0"],["1","1","1"]]', output: '1' }
      ],
      constraints: ['m == grid.length', 'n == grid[i].length', '1 <= m, n <= 300', 'grid[i][j] is "0" or "1"'],
      inputFormat: '2D grid of 0s and 1s.',
      outputFormat: 'Number of islands.',
      platformLink: 'https://leetcode.com/problems/number-of-islands/',
      companies_asked: ['Amazon', 'Facebook', 'Microsoft', 'Bloomberg']
    },
    {
      id: '9',
      title: 'Longest Palindromic Substring',
      slug: 'longest-palindromic-substring',
      difficulty: 'Medium',
      category: 'Strings',
      tags: ['String', 'Dynamic Programming'],
      platform: 'LeetCode',
      description: 'Given a string s, return the longest palindromic substring in s.',
      examples: [
        { input: 's = "babad"', output: '"bab"', explanation: '"aba" is also a valid answer.' },
        { input: 's = "cbbd"', output: '"bb"' }
      ],
      constraints: ['1 <= s.length <= 1000', 's consist of only digits and English letters.'],
      inputFormat: 'A string s.',
      outputFormat: 'Longest palindromic substring.',
      platformLink: 'https://leetcode.com/problems/longest-palindromic-substring/',
      companies_asked: ['Amazon', 'Google', 'Microsoft', 'Facebook']
    },
    {
      id: '10',
      title: 'Container With Most Water',
      slug: 'container-with-most-water',
      difficulty: 'Medium',
      category: 'Two Pointers',
      tags: ['Array', 'Two Pointers', 'Greedy'],
      platform: 'LeetCode',
      description: 'Given n non-negative integers height where each represents a point at coordinate (i, height[i]), find two lines that together with the x-axis form a container that contains the most water.',
      examples: [
        { input: 'height = [1,8,6,2,5,4,8,3,7]', output: '49', explanation: 'The max area is between height[1] and height[8].' }
      ],
      constraints: ['n == height.length', '2 <= n <= 10^5', '0 <= height[i] <= 10^4'],
      inputFormat: 'Array of integers representing heights.',
      outputFormat: 'Maximum area (water).',
      platformLink: 'https://leetcode.com/problems/container-with-most-water/',
      companies_asked: ['Amazon', 'Google', 'Microsoft', 'Facebook']
    },
    {
      id: '11',
      title: 'Word Search',
      slug: 'word-search',
      difficulty: 'Hard',
      category: 'Graphs',
      tags: ['Array', 'Backtracking', 'Depth-First Search', 'Breadth-First Search', 'Matrix'],
      platform: 'LeetCode',
      description: 'Given an m x n grid of characters board and a string word, return true if word exists in the grid.',
      examples: [
        { input: 'board = [["A","B"],["C","D"]], word = "ABCD"', output: 'false', explanation: 'Cannot find ABCD in the grid.' }
      ],
      constraints: ['m == board.length', 'n = board[i].length', '1 <= m, n <= 6', '1 <= word.length <= 15'],
      inputFormat: '2D grid of characters and a word to search.',
      outputFormat: 'true if word exists, false otherwise.',
      platformLink: 'https://leetcode.com/problems/word-search/',
      companies_asked: ['Facebook', 'Microsoft', 'Apple', 'LinkedIn']
    },
    {
      id: '12',
      title: 'Merge K Sorted Lists',
      slug: 'merge-k-sorted-lists',
      difficulty: 'Hard',
      category: 'Linked List',
      tags: ['Linked List', 'Divide and Conquer', 'Heap', 'Priority Queue'],
      platform: 'LeetCode',
      description: 'You are given an array of k linked-lists lists, each linked-list is sorted in ascending order. Merge all the linked-lists into one sorted linked-list and return it.',
      examples: [
        { input: 'lists = [[1,4,5],[1,3,4],[2,6]]', output: '[1,1,2,3,4,4,5,6]' }
      ],
      constraints: ['k == lists.length', '0 <= k <= 10^4', '0 <= lists[i].length <= 500'],
      inputFormat: 'Array of k sorted linked lists.',
      outputFormat: 'One merged sorted linked list.',
      platformLink: 'https://leetcode.com/problems/merge-k-sorted-lists/',
      companies_asked: ['Amazon', 'Google', 'Microsoft', 'Facebook']
    }
  ];
  
  const problem = allProblems.find(p => p.id === id || p.slug === id);
  
  if (!problem) {
    return res.status(404).json({ error: 'Problem not found' });
  }
  
  res.json(problem);
});

// GET /api/topics
// Returns all available topics/categories
app.get('/api/topics', (req, res) => {
  const topics = [
    { value: 'Arrays', label: 'Arrays', count: 2 },
    { value: 'Strings', label: 'Strings', count: 1 },
    { value: 'Algorithms', label: 'Algorithms', count: 0 },
    { value: 'Dynamic Programming', label: 'Dynamic Programming', count: 2 },
    { value: 'Recursion', label: 'Recursion', count: 1 },
    { value: 'Linked List', label: 'Linked List', count: 2 },
    { value: 'Trees', label: 'Trees', count: 1 },
    { value: 'Graphs', label: 'Graphs', count: 2 },
    { value: 'Hash Tables', label: 'Hash Tables', count: 1 },
    { value: 'Greedy', label: 'Greedy', count: 1 },
    { value: 'Two Pointers', label: 'Two Pointers', count: 1 },
    { value: 'Sliding Window', label: 'Sliding Window', count: 0 },
    { value: 'Stack', label: 'Stack', count: 1 },
    { value: 'Queue', label: 'Queue', count: 0 }
  ];
  
  res.json(topics);
});

// GET /api/difficulties
// Returns all available difficulty levels with counts
app.get('/api/difficulties', (req, res) => {
  const difficulties = [
    { value: 'Easy', label: 'Easy', count: 6 },
    { value: 'Medium', label: 'Medium', count: 4 },
    { value: 'Hard', label: 'Hard', count: 2 }
  ];
  
  res.json(difficulties);
});

// POST /api/execute-code (mock)
app.post('/api/execute-code', (req, res) => {
  const { code, language, problem_id } = req.body;
  
  // Mock execution
  setTimeout(() => {
    res.json({
      success: true,
      output: `Running ${language} code...\n\nTest Case 1: PASSED ✓\nTest Case 2: PASSED ✓\nTest Case 3: FAILED ✗\n\nExpected: [0,1]\nGot: [1,0]\n\nTime: 45ms\nMemory: 14.2MB`,
      passed: 2,
      total: 3,
      status: 'partial'
    });
  }, 1000);
});

// ========== VOICE INTERVIEW WEBSOCKET ==========

const interviewQuestions = [
  { type: 'introduction', question: 'Tell me about yourself and your background.' },
  { type: 'technical', question: 'Explain the difference between let, const, and var in JavaScript.' },
  { type: 'dsa', question: 'What is the time complexity of accessing an element in a hash map?' },
  { type: 'system_design', question: 'How would you design a URL shortening service like bit.ly?' },
  { type: 'behavioral', question: 'Tell me about a time you had to debug a difficult problem.' }
];

io.on('connection', (socket) => {
  console.log('Client connected for interview:', socket.id);
  
  let currentQuestion = 0;
  
  socket.on('start_interview', () => {
    currentQuestion = 0;
    socket.emit('question', {
      question: interviewQuestions[0].question,
      type: interviewQuestions[0].type,
      question_number: 1,
      total_questions: interviewQuestions.length,
      instructions: 'Click the microphone button and speak your answer. Click again when done.'
    });
  });
  
  socket.on('submit_answer', (data) => {
    const { answer, transcript } = data;
    
    // Generate feedback based on question type
    const feedback = generateFeedback(interviewQuestions[currentQuestion].type, answer || transcript);
    
    socket.emit('feedback', {
      feedback: feedback.text,
      score: feedback.score,
      tips: feedback.tips
    });
    
    // Send next question after delay
    setTimeout(() => {
      currentQuestion++;
      if (currentQuestion < interviewQuestions.length) {
        socket.emit('question', {
          question: interviewQuestions[currentQuestion].question,
          type: interviewQuestions[currentQuestion].type,
          question_number: currentQuestion + 1,
          total_questions: interviewQuestions.length
        });
      } else {
        socket.emit('interview_complete', {
          message: 'Interview complete! Great job.',
          total_score: Math.floor(Math.random() * 15) + 80
        });
      }
    }, 3000);
  });
  
  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
  });
});

function generateFeedback(type, answer) {
  const responses = {
    introduction: {
      text: 'Good introduction! You covered your background well. Try to be more specific about your achievements and keep it under 2 minutes.',
      score: 85,
      tips: ['Mention specific technologies youve worked with', 'Quantify your impact when possible']
    },
    technical: {
      text: 'Solid technical explanation. You demonstrated good understanding of the concept.',
      score: 88,
      tips: ['Consider mentioning edge cases', 'Practice explaining to non-technical audiences']
    },
    dsa: {
      text: 'Correct answer! O(1) is the right time complexity for hash map access.',
      score: 95,
      tips: ['Also mention space complexity', 'Be ready to explain collision handling']
    },
    system_design: {
      text: 'Good high-level approach. You identified key components well.',
      score: 82,
      tips: ['Discuss trade-offs between different approaches', 'Consider database sharding for scale']
    },
    behavioral: {
      text: 'Great STAR method usage! Your example was clear and relevant.',
      score: 90,
      tips: ['Add more details about the outcome', 'Practice conciseness']
    }
  };
  
  return responses[type] || responses.introduction;
}

// ========== USER PROGRESS ==========

// GET /api/progress/:userId
app.get('/api/progress/:userId', (req, res) => {
  const { userId } = req.params;
  
  // Mock progress data
  res.json({
    progress: {
      interviews_completed: 5,
      average_score: 75,
      problems_solved: 12,
      day_streak: 3,
      recent_activities: [
        { id: '1', type: 'interview', title: 'Mock Interview', description: 'Completed technical interview', timestamp: new Date().toISOString() },
        { id: '2', type: 'practice', title: 'Two Sum', description: 'Solved Easy problem', timestamp: new Date().toISOString() }
      ]
    }
  });
});

// POST /api/start-interview
app.post('/api/start-interview', (req, res) => {
  const { target_role, difficulty, focus_areas } = req.body;
  
  // Create a new interview session
  const sessionId = Date.now().toString();
  const session = {
    id: sessionId,
    target_role: target_role || 'Software Engineer',
    difficulty: difficulty || 'medium',
    focus_areas: focus_areas || ['dsa', 'behavioral'],
    status: 'in_progress',
    current_question_index: 0,
    conversationHistory: [],
    askedQuestions: [],
    started_at: new Date().toISOString(),
    questions_asked: 0,
    max_questions: 5
  };
  interviewSessions.set(sessionId, session);
  
  // Get initial question from the question bank
  const firstArea = session.focus_areas[0];
  const questions = questionBank[firstArea] || questionBank.behavioral;
  const firstQuestion = questions[0];
  
  session.askedQuestions.push(firstQuestion);
  session.conversationHistory.push({ role: 'ai', content: firstQuestion });
  session.questions_asked = 1;
  
  res.json({
    success: true,
    session_id: sessionId,
    question: firstQuestion,
    question_number: 1,
    stage: firstArea,
    stage_label: firstArea.replace('_', ' ').toUpperCase()
  });
});

// POST /api/answer - Submit answer and get next question using Groq AI
app.post('/api/answer', async (req, res) => {
  const { session_id, user_answer, question_id } = req.body;
  
  if (!session_id || !user_answer) {
    return res.status(400).json({ error: 'session_id and user_answer are required' });
  }
  
  const session = interviewSessions.get(session_id);
  if (!session) {
    return res.status(404).json({ error: 'Session not found' });
  }
  
  // Add user's answer to conversation history
  session.conversationHistory.push({ role: 'user', content: user_answer });
  
  // Analyze answer using Groq AI if available
  let analysis = null;
  if (groq) {
    try {
      const lastQuestion = session.conversationHistory.find(m => m.role === 'ai');
      const analysisPrompt = `You are a technical interview evaluator. Analyze this candidate's answer.

Question: ${lastQuestion?.content || 'N/A'}

Candidate's Answer: ${user_answer}

Provide a brief evaluation with:
1. Score (0-100)
2. Strengths (2-3 points)
3. Areas for improvement (2-3 points)

Format as JSON: { "score": number, "strengths": [string], "improvements": [string] }`;

      const completion = await groq.chat.completions.create({
        messages: [
          { role: 'system', content: 'You are a technical interview evaluator.' },
          { role: 'user', content: analysisPrompt }
        ],
        model: 'llama-3.1-8b-instant',
        temperature: 0.3,
        max_tokens: 500
      });
      
      const responseText = completion.choices[0]?.message?.content || '';
      try {
        analysis = JSON.parse(responseText);
      } catch (e) {
        // Fallback if parsing fails
        analysis = { score: 75, strengths: ['Answer provided'], improvements: ['Could be more detailed'] };
      }
    } catch (error) {
      console.error('Groq API error during analysis:', error);
      analysis = { score: 75, strengths: ['Answer provided'], improvements: ['Could be more detailed'] };
    }
  } else {
    // Fallback analysis when Groq is not available
    const wordCount = user_answer.split('\s+').length;
    analysis = {
      score: Math.min(100, 60 + Math.floor(wordCount / 5)),
      strengths: wordCount > 20 ? ['Detailed answer', 'Provided examples'] : ['Answer provided'],
      improvements: wordCount < 20 ? ['Provide more details', 'Give specific examples'] : ['Expand on technical details']
    };
  }
  
  // Check if interview is complete
  if (session.questions_asked >= session.max_questions) {
    interviewSessions.set(session_id, session);
    const finalScore = Math.round(analysis.score);
    return res.json({
      success: true,
      interview_completed: true,
      final_score: finalScore,
      analysis: analysis,
      next_question: null
    });
  }
  
  // Generate next question using Groq AI
  let nextQuestion = null;
  
  if (groq) {
    try {
      // Build context from conversation history
      const historyContext = session.conversationHistory
        .slice(-6)
        .map(m => `${m.role === 'ai' ? 'AI' : 'Candidate'}: ${m.content}`)
        .join('\n');
      
      const nextQuestionPrompt = `You are an expert technical interviewer. Based on the conversation so far, ask the next interview question.

Conversation:
${historyContext}

The candidate just answered: "${user_answer}"

Focus areas: ${session.focus_areas.join(', ')}
Current difficulty: ${session.difficulty}

Ask a NEW question that is different from what has already been asked. Do NOT repeat any question from the conversation history.

Return only the question text, nothing else.`;

      const completion = await groq.chat.completions.create({
        messages: [
          { role: 'system', content: SYSTEM_PROMPTS.interviewer },
          { role: 'user', content: nextQuestionPrompt }
        ],
        model: 'llama-3.1-8b-instant',
        temperature: 0.7,
        max_tokens: 200
      });
      
      nextQuestion = completion.choices[0]?.message?.content?.trim() || '';
    } catch (error) {
      console.error('Groq API error generating next question:', error);
    }
  }
  
  // Fallback to question bank if Groq failed or returned empty
  if (!nextQuestion || session.askedQuestions.includes(nextQuestion)) {
    const remainingQuestions = [];
    for (const area of session.focus_areas) {
      const areaQuestions = questionBank[area] || [];
      for (const q of areaQuestions) {
        if (!session.askedQuestions.includes(q)) {
          remainingQuestions.push(q);
        }
      }
    }
    
    if (remainingQuestions.length > 0) {
      nextQuestion = remainingQuestions[Math.floor(Math.random() * remainingQuestions.length)];
    } else {
      // Use a different question from the bank if all in current focus are used
      const allQuestions = Object.values(questionBank).flat();
      const available = allQuestions.filter(q => !session.askedQuestions.includes(q));
      nextQuestion = available.length > 0 
        ? available[Math.floor(Math.random() * available.length)]
        : "Can you describe a project you've worked on recently?";
    }
  }
  
  // Add to asked questions
  session.askedQuestions.push(nextQuestion);
  session.conversationHistory.push({ role: 'ai', content: nextQuestion });
  session.questions_asked++;
  
  // Determine current stage
  const currentAreaIndex = Math.floor((session.questions_asked - 1) / 2);
  const currentStage = session.focus_areas[currentAreaIndex] || session.focus_areas[0];
  
  interviewSessions.set(session_id, session);
  
  res.json({
    success: true,
    interview_completed: false,
    analysis: analysis,
    next_question: nextQuestion,
    question_number: session.questions_asked,
    current_stage: currentStage,
    stage_label: currentStage.replace('_', ' ').toUpperCase()
  });
});

// POST /api/end-interview - End interview and get evaluation
app.post('/api/end-interview', (req, res) => {
  const { session_id } = req.body;
  
  if (!session_id) {
    return res.status(400).json({ error: 'session_id is required' });
  }
  
  const session = interviewSessions.get(session_id);
  if (!session) {
    return res.status(404).json({ error: 'Session not found' });
  }
  
  // Generate evaluation based on conversation
  const userAnswers = session.conversationHistory.filter(m => m.role === 'user');
  const totalAnswers = userAnswers.length;
  
  const evaluation = {
    overall_score: totalAnswers > 0 ? Math.floor(65 + Math.random() * 25) : 0,
    communication_score: totalAnswers > 0 ? Math.floor(70 + Math.random() * 20) : 0,
    technical_score: totalAnswers > 0 ? Math.floor(65 + Math.random() * 25) : 0,
    total_questions: totalAnswers,
    strengths: [
      'Demonstrated problem-solving skills',
      'Clear communication of ideas',
      'Technical knowledge breadth'
    ],
    improvements: [
      'Could provide more specific examples',
      'Consider edge cases in answers',
      'Work on concise explanations'
    ],
    category_scores: {
      dsa: Math.floor(60 + Math.random() * 30),
      oop: Math.floor(60 + Math.random() * 30),
      system_design: Math.floor(60 + Math.random() * 30),
      behavioral: Math.floor(70 + Math.random() * 20)
    },
    suggestions: [
      'Practice system design questions regularly',
      'Review data structure implementations',
      'Prepare concrete examples from your experience'
    ]
  };
  
  // Clean up session
  session.status = 'completed';
  session.evaluation = evaluation;
  interviewSessions.set(session_id, session);
  
  res.json({
    success: true,
    session_id: session_id,
    evaluation: evaluation
  });
});

// POST /api/interview - New unified endpoint for AI-powered interview
app.post('/api/interview', async (req, res) => {
  const { answer, conversationHistory } = req.body;
  
  // If no conversation history, this is the start of interview
  if (!conversationHistory || conversationHistory.length === 0) {
    // Start new interview
    const sessionId = Date.now().toString();
    const focusAreas = ['dsa', 'oop', 'system_design', 'behavioral'];
    
    const session = {
      id: sessionId,
      focus_areas: focusAreas,
      status: 'in_progress',
      conversationHistory: [],
      askedQuestions: [],
      questions_asked: 0,
      max_questions: 5
    };
    interviewSessions.set(sessionId, session);
    
    // Get first question
    const firstArea = focusAreas[0];
    const questions = questionBank[firstArea] || questionBank.behavioral;
    const firstQuestion = questions[0];
    
    session.askedQuestions.push(firstQuestion);
    session.conversationHistory.push({ role: 'ai', content: firstQuestion });
    session.questions_asked = 1;
    interviewSessions.set(sessionId, session);
    
    return res.json({
      session_id: sessionId,
      question: firstQuestion,
      question_number: 1,
      stage: firstArea
    });
  }
  
  // Process answer and get next question
  const sessionId = req.body.session_id || Date.now().toString();
  let session = interviewSessions.get(sessionId);
  
  if (!session) {
    session = {
      id: sessionId,
      focus_areas: ['dsa', 'oop', 'system_design', 'behavioral'],
      status: 'in_progress',
      conversationHistory: [],
      askedQuestions: [],
      questions_asked: 0,
      max_questions: 5
    };
  }
  
  // Add answer to history
  if (answer) {
    session.conversationHistory.push({ role: 'user', content: answer });
  }
  
  // Check if complete
  if (session.questions_asked >= session.max_questions) {
    return res.json({
      interview_completed: true,
      message: 'Interview completed!'
    });
  }
  
  // Generate next question using Groq
  let nextQuestion = null;
  
  if (groq) {
    try {
      const historyContext = session.conversationHistory
        .slice(-6)
        .map(m => `${m.role === 'ai' ? 'AI' : 'Candidate'}: ${m.content}`)
        .join('\n');
      
      const prompt = `You are a technical interviewer. Based on this conversation:

${historyContext}

Ask the next interview question about ${session.focus_areas.join(', ')}. 
Do NOT repeat any previous questions. Be specific and professional.

Return ONLY the question text.`;

      const completion = await groq.chat.completions.create({
        messages: [{ role: 'user', content: prompt }],
        model: 'llama-3.1-8b-instant',
        temperature: 0.7,
        max_tokens: 150
      });
      
      nextQuestion = completion.choices[0]?.message?.content?.trim();
    } catch (error) {
      console.error('Groq API error:', error);
    }
  }
  
  // Fallback
  if (!nextQuestion || session.askedQuestions.includes(nextQuestion)) {
    const allQuestions = Object.values(questionBank).flat();
    const available = allQuestions.filter(q => !session.askedQuestions.includes(q));
    nextQuestion = available.length > 0
      ? available[Math.floor(Math.random() * available.length)]
      : "Can you explain a recent technical challenge you faced?";
  }
  
  session.askedQuestions.push(nextQuestion);
  session.conversationHistory.push({ role: 'ai', content: nextQuestion });
  session.questions_asked++;
  interviewSessions.set(sessionId, session);
  
  res.json({
    session_id: sessionId,
    question: nextQuestion,
    question_number: session.questions_asked
  });
});

// SYSTEM_PROMPTS for interview
const SYSTEM_PROMPTS = {
  interviewer: `You are an expert technical interviewer at a top tech company.
Ask clear, professional interview questions.
Focus on: ${['dsa', 'oop', 'system_design', 'behavioral'].join(', ')}
Be encouraging but rigorous.
Evaluate technical accuracy, problem-solving, and communication.`
};

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Start server
server.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
  console.log(`Uploads directory: ${uploadsDir}`);
});



