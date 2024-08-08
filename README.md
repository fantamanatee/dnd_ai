# DnD_AI 🐉✨

Welcome to DnD_AI, the ultimate WebApp for Dungeons and Dragons enthusiasts to create and interact with AI characters!

## Current Deployment
🔗 **Try it out!** [DnD AI]([https://tinyurl.com/DnD-bot-ai](https://charming-ganache-286033.netlify.app/))

## Architecture
The back end harnesses the power of LangChain and OpenAI's API to deliver robust chatbot functionality. Character, session, and bot data are securely stored in MongoDB.

The front end is written from scratch using TypeScript, HTML, and CSS for a seamless user experience.

The default chatbot is based on LangChain's tutorial: [qa with chat history](https://python.langchain.com/v0.1/docs/use_cases/question_answering/chat_history/)

The advanced reasoning agent is based on this paper for creating interactive agents using architectural and interaction patterns for enabling
believable simulations of human behavior: [Generative Agents: Interactive Simulacra of Human Behavior](https://arxiv.org/abs/2304.03442).

All interactions are handled via a RESTful API.

### Deployment Details
- **Backend Hosting**: Render.com
- **Frontend Hosting**: Netlify
- **Database**: MongoDB Atlas cluster

### References:
- Park, J. S., O'Brien, J. C., Cai, C. J., Morris, M. R., Liang, P., & Bernstein, M. S. (2023). *Generative agents: Interactive simulacra of human behavior*. arXiv. https://arxiv.org/abs/2304.03442

## License
📜 [MIT License](https://choosealicense.com/licenses/mit/)
