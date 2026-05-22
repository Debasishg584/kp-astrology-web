# Deployment Guide / ওয়েবসাইট হোস্টিং গাইড

This folder (`kp_astrology_web`) is now 100% self-contained and contains all calculations, predictions, and ephemeris backend engines. You can deploy it online to a dedicated free website.

এই ফোল্ডারটি (`kp_astrology_web`) এখন সম্পূর্ণ স্বয়ংসম্পূর্ণ এবং এতে সমস্ত গণনা, পূর্বাভাস এবং এফিমেরিস ব্যাকএন্ড ইঞ্জিন রয়েছে। আপনি এটিকে ইন্টারনেটে একটি ডেডিকেটেড ফ্রি ওয়েবসাইটে হোস্ট করতে পারেন।

---

## Option 1: Deploy on Render.com (Recommended & Fully Automated)
### রেন্ডার ডট কম-এ হোস্টিং (সবচেয়ে সহজ ও স্বয়ংক্রিয়)

1. **Upload to GitHub (গিটহাবে আপলোড করুন):**
   * Create a private or public repository on [GitHub](https://github.com).
   * Push all files in `C:\Users\Debasish\Desktop\kp_astrology_web` to your repository.
   * *গিটহাবে একটি নতুন রিপোজিটরি তৈরি করুন এবং এই ফোল্ডারের সমস্ত ফাইল সেখানে আপলোড করুন।*

2. **Connect to Render (রেন্ডারে যুক্ত করুন):**
   * Go to [Render](https://render.com) and create a free account.
   * Click **New +** and select **Web Service**.
   * Connect your GitHub account and select your repository.
   * *Render.com এ গিয়ে একটি ফ্রি অ্যাকাউন্ট তৈরি করুন। New + বাটনে ক্লিক করে Web Service সিলেক্ট করুন এবং আপনার গিটহাব রিপোজিটরিটি যুক্ত করুন।*

3. **Configure Settings (কনফিগারেশন):**
   * **Name:** `divya-drishti` (or any name you like)
   * **Runtime:** `Python`
   * **Build Command:** `pip install -r requirements.txt`
   * **Start Command:** `gunicorn web_app:app`
   * **Instance Type:** `Free`
   * Click **Deploy Web Service**.
   * *সেটিংসগুলো পূরণ করে Deploy Web Service বাটনে ক্লিক করুন। ২-৩ মিনিটের মধ্যে আপনার সাইট লাইভ হয়ে যাবে এবং আপনি একটি ফ্রি পাবলিক লিংক (যেমন: `https://divya-drishti.onrender.com`) পেয়ে যাবেন।*

---

## Option 2: Deploy on PythonAnywhere.com
### পাইথন অ্যানিহোয়ার-এ হোস্টিং

1. **Sign Up (অ্যাকাউন্ট তৈরি করুন):**
   * Create a free account at [PythonAnywhere](https://www.pythonanywhere.com).
   * Your URL will be `yourusername.pythonanywhere.com`.
   * *PythonAnywhere-এ একটি ফ্রি অ্যাকাউন্ট তৈরি করুন।*

2. **Upload Files (ফাইল আপলোড করুন):**
   * Go to the **Files** tab and upload your files, or zip the folder and upload it, then unzip it via the Bash console.
   * *Files ট্যাবে গিয়ে আপনার জিপ ফোল্ডারটি আপলোড করুন এবং কনসোল থেকে আনজিপ করুন।*

3. **Configure Web App (ওয়েব অ্যাপ সেটিংস):**
   * Go to the **Web** tab, click **Add a new web app**.
   * Choose **Flask** and select **Python 3.10**.
   * Set the path to `web_app.py` in your uploaded directory.
   * In the WSGI configuration file, make sure the environment points to your directory and loads `app`.
   * *Web ট্যাবে গিয়ে Flask সিলেক্ট করুন এবং আপনার আপলোড করা ফাইলের পাথ বসিয়ে দিন।*

4. **Install Dependencies (ডিপেন্ডেন্সি ইনস্টল):**
   * Open a **Bash Console** and run:
     ```bash
     pip install --user -r requirements.txt
     ```
   * Reload your web app, and it will be live!
   * *কনসোল থেকে লাইব্রেরিগুলো ইনস্টল করার পর রিলোড দিলেই আপনার ওয়েবসাইট চালু হয়ে যাবে।*
