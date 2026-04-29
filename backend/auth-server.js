const express = require('express');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 8001;
const JWT_SECRET = 'your-jwt-secret-key-change-in-production';

// Middleware
app.use(cors());
app.use(express.json());

// Simple JSON file-based database
const DB_FILE = path.join(__dirname, 'users.json');

// Helper functions
function readUsers() {
  try {
    if (!fs.existsSync(DB_FILE)) {
      return [];
    }
    const data = fs.readFileSync(DB_FILE, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    console.error('Error reading users:', error);
    return [];
  }
}

function writeUsers(users) {
  try {
    fs.writeFileSync(DB_FILE, JSON.stringify(users, null, 2));
    return true;
  } catch (error) {
    console.error('Error writing users:', error);
    return false;
  }
}

function findUserByEmail(email) {
  const users = readUsers();
  return users.find(u => u.email === email);
}

function findUserById(id) {
  const users = readUsers();
  return users.find(u => u.id === id);
}

// Routes

// POST /register - Create new user
app.post('/auth/register', async (req, res) => {
  try {
    const { email, password, full_name } = req.body;

    // Validation
    if (!email || !password || !full_name) {
      return res.status(400).json({ detail: 'Email, password, and name are required' });
    }

    // Check if user exists
    const existingUser = findUserByEmail(email);
    if (existingUser) {
      return res.status(400).json({ detail: 'User with this email already exists' });
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Create user
    const newUser = {
      id: Date.now().toString(),
      email,
      password: hashedPassword,
      full_name,
      created_at: new Date().toISOString()
    };

    // Save user
    const users = readUsers();
    users.push(newUser);
    writeUsers(users);

    // Generate token
    const token = jwt.sign(
      { user_id: newUser.id, email: newUser.email },
      JWT_SECRET,
      { expiresIn: '7d' }
    );

    res.status(201).json({
      access_token: token,
      user: {
        id: newUser.id,
        email: newUser.email,
        full_name: newUser.full_name
      }
    });
  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({ detail: 'Registration failed' });
  }
});

// POST /login - Authenticate user
app.post('/auth/login', async (req, res) => {
  try {
    const { email, password } = req.body;

    // Validation
    if (!email || !password) {
      return res.status(400).json({ detail: 'Email and password are required' });
    }

    // Find user
    const user = findUserByEmail(email);
    if (!user) {
      return res.status(401).json({ detail: 'Invalid email or password' });
    }

    // Verify password
    const isValidPassword = await bcrypt.compare(password, user.password);
    if (!isValidPassword) {
      return res.status(401).json({ detail: 'Invalid email or password' });
    }

    // Generate token
    const token = jwt.sign(
      { user_id: user.id, email: user.email },
      JWT_SECRET,
      { expiresIn: '7d' }
    );

    res.json({
      access_token: token,
      user: {
        id: user.id,
        email: user.email,
        full_name: user.full_name
      }
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ detail: 'Login failed' });
  }
});

// GET /auth/me - Get current user
app.get('/auth/me', (req, res) => {
  try {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ detail: 'No token provided' });
    }

    const token = authHeader.split(' ')[1];
    const decoded = jwt.verify(token, JWT_SECRET);

    const user = findUserById(decoded.user_id);
    if (!user) {
      return res.status(401).json({ detail: 'User not found' });
    }

    res.json({
      id: user.id,
      email: user.email,
      full_name: user.full_name
    });
  } catch (error) {
    res.status(401).json({ detail: 'Invalid token' });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`Auth server running on http://localhost:${PORT}`);
});
