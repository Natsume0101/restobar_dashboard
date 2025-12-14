# How to Deploy to Streamlit Community Cloud

Your project is now git-ready (`requirements.txt` created, git repo initialized).

## Step 1: Push to GitHub
1.  **Create a New Repository** on [GitHub.com](https://github.com/new).
    *   Name it: `restobar-dashboard`.
    *   Do **NOT** add README, gitignore, or license (we already have them).
2.  **Push your code**:
    Open your terminal in this folder (`c:\Users\julie\.gemini\antigravity\proyecto_datos`) and run:
    ```bash
    git remote add origin https://github.com/YOUR_USERNAME/restobar-dashboard.git
    git branch -M main
    git push -u origin main
    ```
    *(Replace `YOUR_USERNAME` with your actual GitHub username)*

## Step 2: Deploy on Streamlit Cloud
1.  Go to [share.streamlit.io](https://share.streamlit.io/).
2.  Click **"New app"**.
3.  Select **"Use existing repo"**.
4.  Choose your repository: `YOUR_USERNAME/restobar-dashboard`.
5.  **Main file path**: `dashboard.py`.
6.  Click **"Deploy!"**.

Streamlit will automatically install dependencies from `requirements.txt` and launch your app.
