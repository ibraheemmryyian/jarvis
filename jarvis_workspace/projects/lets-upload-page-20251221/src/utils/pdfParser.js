const pdfParse = require('pdf-parse');

async function parsePDF(fileBuffer) {
  try {
    const data = await pdfParse(fileBuffer);
    return {
      text: data.text,
      pages: data.numpages,
      metadata: extractMetadata(data.text)
    };
  } catch (error) {
    throw new Error('Failed to parse PDF');
  }
}

function extractMetadata(text) {
  const lines = text.split('\n');
  const metadata = {
    title: '',
    author: '',
    pageCount: 0,
    keywords: [],
    targetAudience: '',
    summary: ''
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (line.startsWith('Title:')) {
      metadata.title = line.replace('Title:', '').trim();
    } else if (line.startsWith('Author:')) {
      metadata.author = line.replace('Author:', '').trim();
    } else if (line.startsWith('Page Count:')) {
      metadata.pageCount = parseInt(line.replace('Page Count:', '').trim());
    } else if (line.startsWith('Keywords:')) {
      metadata.keywords = line.replace('Keywords:', '').trim().split(',').map(k => k.trim());
    } else if (line.startsWith('Target Audience:')) {
      metadata.targetAudience = line.replace('Target Audience:', '').trim();
    } else if (line.startsWith('Summary:')) {
      metadata.summary = line.replace('Summary:', '').trim();
    }
  }

  return metadata;
}

module.exports = { parsePDF, extractMetadata };
```

```javascript