# CIIS Press Release Generator

The CIIS Press Release Generator is an application based on Streamlit and OpenAI technologies designed to help the Chinese Innovation and Invention Society (CIIS) create high-quality press releases. Users can choose an upcoming invention exhibition and provide relevant exhibition and award-winning invention details, and the system will automatically generate a detailed press release.

## Features

- **Secure Login**: Ensure only authorized users can access the application with a password-protection feature.
- **Exhibition Information Selection**: Users can select an upcoming invention exhibition from a dropdown menu.
- **Automatic Press Release Generation**: Automatically generate a professional press release based on provided exhibition and invention details.
- **Real-Time Display and Download**: Display the generated press release instantly and provide a download option.

## Installation and Setup

### Setup env variables in Heroku

```
heroku config:set -a ciis-genai OPENAI_API_KEY='sk-...'
heroku config:set -a ciis-genai PASSWORD='...'
```

## Usage

1. Start the application:

   ```sh
   streamlit run app.py
   ```

2. Open the application page in your browser and enter the password to log in.

3. Select an invention exhibition and provide relevant exhibition and award-winning invention details.

4. Click the button to generate the press release, and the application will automatically generate and display the result.

5. You can download the generated press release as a text file.
