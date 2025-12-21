function generateEmail(metadata, recipientType) {
  const subject = recipientType === 'C-suite' 
    ? 'Waste Valorization Strategy for Your Business'
    : 'Waste Valorization Guide for SMEs — Maximize Returns, Minimize Waste';

  const body = `
    <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1e1e1e; color: #e0e0e0; padding: 20px; border-radius: 8px;">

      <h2 style="font-size: 1.8rem; margin-bottom: 20px; color: #4caf50;">${metadata.title}</h2>

      <p style="margin-bottom: 20px;">Hello ${recipientType === 'C-suite' ? 'Executive Leadership' : 'SME Team'},</p>

      <p style="margin-bottom: 20px;">I recently came across your company's waste management practices and wanted to share a comprehensive guide on waste valorization — a strategy that not only reduces environmental impact but also generates significant financial returns.</p>

      <p style="margin-bottom: 20px;">This 14-page report includes:</p>

      <ul style="margin-bottom: 20px; padding-left: 20px;">
        <li>Practical steps to implement waste valorization</li>
        <li>Case studies from leading industries</li>
        <li>ROI projections and cost-saving strategies</li>
      </ul>

      <p style="margin-bottom: 20px;">Download the guide here: <a href="https://example.com/download" style="color: #4caf50; text-decoration: none;">Download Now</a></p>

      <p style="margin-bottom: 20px;">Let me know if you'd like to schedule a call to discuss how this can be tailored to your business.</p>

      <p style="margin-bottom: 20px;">Best regards,<br>
      GreenTech Solutions</p>

      <p style="font-size: 0.9rem; color: #b3b3b3; margin-top: 20px;">Waste valorization isn’t just sustainable — it’s profitable. Start today.</p>

      <p style="font-size: 0.9rem; color: #b3b3b3; margin-top: 10px;">*This email was automatically generated based on your uploaded document.*</p>

    </div>
  `;

  return {
    subject,
    body
  };
}

module.exports = { generateEmail };
```

```javascript
// server/api/send.js
const express = require('express');
const router = express.Router();
const { sendEmail } = require('../utils/emailSender');

router.post('/', async (req, res) => {
  const { email_id, recipient_type, send_status } = req.body;

  try {
    const result = await sendEmail(email_id, recipient_type, send_status);
    res.status(200).json({ status: 'success', message: 'Email sent successfully', data: result });
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
});

module.exports = router;
```

```javascript
// server/index.js
const express = require('express');
const cors = require('cors');
const path = require('path');
const app = express();

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// API routes
const sendRouter = require('./api/send');
app.use('/api/send', sendRouter);

// Serve static files
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

```javascript