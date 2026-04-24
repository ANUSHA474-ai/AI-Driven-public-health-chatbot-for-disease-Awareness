# 🚀 QUICK START GUIDE

Get your AI Health Chatbot running in **3 simple steps**!

---

## ⚡ SUPER QUICK START

### Windows Users:
1. **Double-click** `install.bat` → Installs everything automatically
2. **Run** `python app.py`
3. **Open browser** → http://localhost:5000

### Mac/Linux Users:
1. **Run** `./install.sh` → Installs everything automatically
2. **Run** `python3 app.py`
3. **Open browser** → http://localhost:5000

---

## 📋 MANUAL INSTALLATION

### Step 1: Install Dependencies
```bash
# Windows
pip install -r requirements.txt

# Mac/Linux
pip3 install -r requirements.txt
```

### Step 2: Start the Server
```bash
# Windows
python app.py

# Mac/Linux
python3 app.py
```

### Step 3: Open Browser
```
http://localhost:5000
```

**That's it! You're ready to go!** 🎉

---

## 🧪 QUICK TEST

Once the app is running:

1. **Type these symptoms:**
   ```
   itching skin rash nodal skin eruptions
   ```

2. **Click "Analyze Symptoms"**

3. **You should see:**
   - Disease: **Fungal infection**
   - Confidence: **75-85%**
   - Complete disease information

---

## 🎤 TEST VOICE INPUT

1. Click the **🎤 Speak** button
2. Allow microphone access
3. Say: *"fever cough headache"*
4. Click **Analyze Symptoms**

---

## 🌍 TEST LANGUAGES

1. Click language dropdown (top right)
2. Select **Español** or **中文**
3. UI updates to selected language
4. Voice input also changes language!

---

## ⚡ QUICK EXAMPLES

Click the quick example buttons to test:
- Fungal infection
- Dengue
- Migraine

---

## 🔧 TROUBLESHOOTING

**Problem: Port 5000 already in use**
```python
# Edit app.py (last line)
app.run(debug=True, host='0.0.0.0', port=5001)
```

**Problem: Module not found**
```bash
pip install Flask flask-cors pandas numpy scikit-learn
```

**Problem: Voice not working**
- Use Chrome, Edge, or Safari
- Allow microphone permissions
- Check browser console for errors

---

## 📊 WHAT TO EXPECT

**On Startup, you'll see:**
```
======================================================================
🏥 AI Health Chatbot - Enhanced Accuracy Version
======================================================================
✓ Loaded 41 diseases
✓ Model trained successfully

📊 Model Evaluation:
   KNN Accuracy: 85.32% (±3.45%)
   Random Forest Accuracy: 88.76% (±2.91%)

✓ Models trained successfully
✓ Feature dimensions: 2000

======================================================================
✅ SERVER READY
======================================================================

🌐 Server starting on http://localhost:5000
```

---

## 🎯 SYSTEM REQUIREMENTS

**Minimum:**
- Python 3.8+
- 2GB RAM
- 500MB free space
- Modern browser

**Recommended:**
- Python 3.10+
- 4GB RAM
- Chrome/Edge browser

---

## 📱 MOBILE ACCESS

1. Find your computer's IP address:
   ```bash
   # Windows
   ipconfig
   
   # Mac/Linux
   ifconfig
   ```

2. On your phone, visit:
   ```
   http://YOUR_IP_ADDRESS:5000
   ```

Example: `http://192.168.1.100:5000`

---

## 🎓 LEARNING RESOURCES

**After you get it running:**

1. Check the **README.md** for full documentation
2. Explore the **API endpoints** at `/api/diseases`
3. View **source code** to learn ML implementation
4. Read **comments** in app.py for understanding

---

## 🆘 NEED HELP?

1. ✅ Check `README.md` for detailed documentation
2. ✅ Check this guide for quick solutions
3. ✅ Review error messages in terminal
4. ✅ Ensure all files extracted correctly

---

## 🎉 YOU'RE READY!

**Start the app and begin predicting diseases!**

```bash
python app.py
```

**Then visit:** http://localhost:5000

**Happy health monitoring! 🏥**
