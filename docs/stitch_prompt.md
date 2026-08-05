# Prompt for Google Stitch

Copy and paste the following prompt into Google Stitch to generate your frontend application:

***

**Build a modern, sleek chat interface for a Mutual Fund FAQ Assistant.** 

**Design & Theme:**
- The app should look highly professional, trustworthy, and clean (financial theme). Use a clean white/light gray background with teal/green accents (similar to Groww's brand colors) or deep blue.
- Ensure the layout is responsive and looks great on both desktop and mobile.
- Use Tailwind CSS for styling and Lucide React for icons.

**Layout Structure:**
1. **Header (Top):**
   - App Title: "Groww Mutual Fund Assistant".
   - Include a small, subtle badge next to the title that says "Facts Only".
2. **Main Chat Area (Middle):**
   - When the chat is empty, display a **Welcome Panel**. It should have a friendly greeting (e.g., "Hi! Ask me anything about our mutual funds.") and 3 clickable suggestion cards:
     - *"What is the expense ratio of HDFC Mid-Cap Opportunities Fund?"*
     - *"What is the minimum SIP amount for Axis Small Cap?"*
     - *"Who is the fund manager for Nippon India Small Cap?"*
   - When there are messages, display a threaded conversation.
   - User messages should be aligned to the right (distinct background color).
   - Assistant messages should be aligned to the left. The assistant's text must support basic markdown rendering (specifically bold text and clickable hyperlinks, as citations will be returned as URLs).
3. **Input Area (Bottom):**
   - A modern text input field with placeholder text "Ask a question about mutual funds...".
   - A send icon/button. It should be disabled when the input is empty or when waiting for a response.
4. **Footer (Very Bottom):**
   - A persistent, centered disclaimer text in small font: *"Disclaimer: Facts-only. This bot does not provide investment advice."*

**Interactions & Logic:**
- Clicking any of the 3 suggestion cards should immediately populate the input and send the message.
- Hitting "Enter" or clicking the send button should add the user's message to the chat and immediately show a visual loading state (like a pulsing "thinking..." indicator) for the assistant.
- **API Integration:** To get the assistant's reply, make a `POST` request to `http://localhost:8000/api/chat` with a JSON body: `{ "query": "<user_input>" }`.
- Expect a JSON response in this format: `{ "response": "<assistant_markdown_text>" }`.
- Append the `response` text to the chat as the assistant's message and remove the loading state. (If the fetch fails, show a generic error message bubble).

Please generate the complete, fully functional UI based on these requirements.
