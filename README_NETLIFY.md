# How to Deploy to Netlify

You have a special folder prepared for deployment: `deployment`.
This folder contains a "Serverless" version of your dashboard that runs entirely in the browser.

## Steps to Publish

1.  **Open Netlify Drop**: Go to [https://app.netlify.com/drop](https://app.netlify.com/drop).
2.  **Locate Folder**: Open your workspace folder: `c:\Users\julie\.gemini\antigravity\proyecto_datos`.
3.  **Drag & Drop**: Drag the `deployment` folder **entirely** onto the Netlify drop zone.
4.  **Wait**: Netlify will upload the files (approx 3 files).
5.  **View**: Once finished, Netlify will give you a public URL (e.g., `https://random-name.netlify.app`).

## Troubleshooting
- If the app stays "Loading..." for more than 1 minute, check the browser console (F12) for errors.
- Ensure that `ventas_historicas_3anos.csv` was correctly copied to the deployment folder.
