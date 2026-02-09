blaaaah
======

Small desktop app (MVP) built with PySide6.

Features
--------

- Bullet-style text editor for notes
- GitHub integration via OAuth
- Local persistence of notes and preferences

Quickstart
---------

1. Install dependencies (recommended: poetry):

   poetry install

2. Set up GitHub OAuth App (required for GitHub login):

   a. Go to https://github.com/settings/developers
   b. Click "New OAuth App" or "Register a new application"
   c. Fill in the application details:
      - Application name: blaaaah (or any name you prefer)
      - Homepage URL: https://github.com/yourusername/blaaaah (use your repository URL)
      - Authorization callback URL: https://github.com/yourusername/blaaaah (device flow doesn't require callbacks)
   d. Click "Register application"
   e. Copy the "Client ID" from the app page
   f. **Option 1**: Set as environment variable:
      ```
      export GITHUB_CLIENT_ID=your_client_id_here
      ```
   g. **Option 2**: Configure in the app's Settings screen after launching

3. Run the app:

   poetry run blaaaah

4. If you didn't set the environment variable, click Settings and enter your GitHub Client ID

5. Click "Sign into GitHub" on the Welcome screen

6. Follow the device flow instructions to authorize the app

Project layout
--------------

- src/blaaaah: application source
- assets: icons and placeholders

Notes
-----
This scaffold implements the app shell, Welcome, Editor, Paste Repo, and Settings screens with local persistence.

The app uses GitHub's device flow for OAuth authentication, which is perfect for desktop applications.
Your GitHub token is securely stored in your system's keyring.
