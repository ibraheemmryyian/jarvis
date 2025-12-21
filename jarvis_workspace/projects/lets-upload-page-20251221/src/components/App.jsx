import React, { useState } from 'react';
import UploadForm from './UploadForm';
import EmailPreview from './EmailPreview';

function App() {
  const [pdfFile, setPdfFile] = useState(null);
  const [emailData, setEmailData] = useState(null);
  const [recipientType, setRecipientType] = useState('C-suite');

  const handleFileUpload = (file) => {
    setPdfFile(file);
  };

  const handleGenerateEmail = async () => {
    if (!pdfFile) {
      alert('Please upload a PDF file');
      return;
    }

    try {
      const pdfBuffer = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = reject;
        reader.readAsArrayBuffer(file);
      });

      const { text, metadata } = await parsePDF(pdfBuffer);
      const email = generateEmail(metadata, recipientType);

      setEmailData(email);
    } catch (error) {
      alert('Failed to generate email. Please try again.');
    }
  };

  return (
    <div className="container">
      <header className="header">
        <h1>Waste Valorization Email Generator</h1>
        <p>Upload your 14-page PDF and generate a professional cold outreach email for C-suite and SMEs</p>
      </header>

      <UploadForm onFileUpload={handleFileUpload} />

      <button className="btn" onClick={handleGenerateEmail}>
        Generate Email
      </button>

      {emailData && (
        <EmailPreview emailData={emailData} />
      )}
    </div>
  );
}

export default App;
```

```javascript