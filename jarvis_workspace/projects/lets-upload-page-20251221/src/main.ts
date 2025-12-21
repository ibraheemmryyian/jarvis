// Fixed POST request to /api/search
const searchNotes = async (query: string, filters: { dateRange?: string; tag?: string }) => {
  const mockNotes = [
    {
      id: 1,
      title: "Meeting Notes",
      content: "Discussed Q4 goals and resource allocation.",
      createdAt: "2025-12-15T10:30:00Z",
      tags: ["meeting", "q4"]
    },
    {
      id: 2,
      title: "Project Update",
      content: "Backend API is ready for integration.",
      createdAt: "2025-12-14T14:20:00Z",
      tags: ["backend", "api"]
    },
    {
      id: 3,
      title: "Team Lunch",
      content: "Everyone enjoyed the pizza!",
      createdAt: "2025-12-13T12:00:00Z",
      tags: ["team", "lunch"]
    }
  ];

  let filteredNotes = mockNotes;

  if (filters.tag) {
    filteredNotes = filteredNotes.filter(note => note.tags.includes(filters.tag));
  }

  if (filters.dateRange) {
    const [start, end] = filters.dateRange.split(' to ');
    filteredNotes = filteredNotes.filter(note => {
      const noteDate = new Date(note.createdAt);
      const startDate = new Date(start);
      const endDate = new Date(end);
      return noteDate >= startDate && noteDate <= endDate;
    });
  }

  if (query) {
    filteredNotes = filteredNotes.filter(note =>
      note.title.toLowerCase().includes(query.toLowerCase()) ||
      note.content.toLowerCase().includes(query.toLowerCase())
    );
  }

  return filteredNotes;
};

{
  id: string,
  name: string,
  subject: string,
  body: string,
  targetAudience: "C-suite" | "SME",
  createdAt: string
}

{
  id: "email-csuite-001",
  name: "Q4 Goals Summary",
  subject: "Q4 Goals & Resource Allocation Summary",
  body: `Hi Team,

This is a summary of our Q4 goals and resource allocation discussed in today’s meeting.

📌 Key Points:
- Primary focus: Deliver core product features by end of Q4.
- Resource allocation: 60% of team capacity dedicated to backend development.
- Cross-functional collaboration required for UX and QA.

📅 Date: December 15, 2025
🔗 View Full Notes: [Link to Notes]

Let’s align on next steps by EOD.

Best regards,  
[Your Name]`,
  targetAudience: "C-suite",
  createdAt: "2025-12-15T10:30:00Z"
}

{
  id: "email-sme-001",
  name: "Q4 Goals Summary for SMEs",
  subject: "Q4 Goals & Resource Allocation — Action Items for SMEs",
  body: `Hi [First Name],

Here’s a quick update on Q4 goals and resource allocation from our recent meeting.

📌 Action Items for You:
- Backend team: Ensure API readiness by Dec 20.
- UX team: Provide wireframes for Q4 features by Dec 18.
- QA team: Begin test planning for Q4 deliverables.

📅 Date: December 15, 2025
🔗 View Full Notes: [Link to Notes]

Please reach out if you need clarification or support.

Thanks,  
[Your Name]`,
  targetAudience: "SME",
  createdAt: "2025-12-15T10:30:00Z"
}

// OutreachEmail Schema Definition for the Web App
export interface OutreachEmail {
  id: string;
  reportId: string;
  userId: string;
  templateId: string;
  recipient: string;
  subject: string;
  body: string;
  sentAt: string | null;
  status: 'draft' | 'sent' | 'failed';
}

// Email Templates for C-suite and SME
export const emailTemplates = {
  'email-csuite-001': {
    id: 'email-csuite-001',
    name: 'Q4 Goals Summary',
    subject: 'Q4 Goals & Resource Allocation Summary',
    body: `Hi Team,

This is a summary of our Q4 goals and resource allocation discussed in today’s meeting.

📌 Key Points:
- Primary focus: Deliver core product features by end of Q4.
- Resource allocation: 60% of team capacity dedicated to backend development.
- Cross-functional collaboration required for UX and QA.

📅 Date: December 15, 2025
🔗 View Full Notes: [Link to Notes]

Let’s align on next steps by EOD.

Best regards,  
[Your Name]`,
    targetAudience: 'C-suite',
    createdAt: '2025-12-15T10:30:00Z'
  },
  'email-sme-001': {
    id: 'email-sme-001',
    name: 'Q4 Goals Summary for SMEs',
    subject: 'Q4 Goals & Resource Allocation — Action Items for SMEs',
    body: `Hi [First Name],

Here’s a quick update on Q4 goals and resource allocation from our recent meeting.

📌 Action Items for You:
- Backend team: Ensure API readiness by Dec 20.
- UX team: Provide wireframes for Q4 features by Dec 18.
- QA team: Begin test planning for Q4 deliverables.

📅 Date: December 15, 2025
🔗 View Full Notes: [Link to Notes]

Please reach out if you need clarification or support.

Thanks,  
[Your Name]`,
    targetAudience: 'SME',
    createdAt: '2025-12-15T10:30:00Z'
  }
};

// Utility function to generate an OutreachEmail based on template and recipient type
function generateOutreachEmail(
  reportId: string,
  userId: string,
  recipient: string,
  templateId: string
): OutreachEmail {
  const template = emailTemplates[templateId];
  if (!template) {
    throw new Error(`Template with ID ${templateId} not found`);
  }

  const subject = template.subject;
  const body = template.body
    .replace('[Your Name]', `${userId} (from Waste Valorization Report #${reportId})`)
    .replace('[First Name]', recipient.split(' ')[0] || 'Team');

  return {
    id: `email-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    reportId,
    userId,
    templateId,
    recipient,
    subject,
    body,
    sentAt: null,
    status: 'draft'
  };
}

// Example usage
const sampleEmail = generateOutreachEmail(
  'report-001',
  'user-001',
  'John Doe',
  'email-csuite-001'
);

console.log(sampleEmail);

interface User {
  id: string;
  name: string;
  email: string;
  avatar: string;
  preferences: {
    theme: 'dark' | 'light';
    language: 'en' | 'es' | 'fr';
    notificationPreferences: {
      email: boolean;
      inApp: boolean;
    };
  };
  createdAt: Date;
  updatedAt: Date;
}

interface User {
  id: string;
  name: string;
  email: string;
  avatar: string;
  preferences: {
    theme: 'dark' | 'light';
    language: 'en' | 'es' | 'fr';
    notificationPreferences: {
      email: boolean;
      inApp: boolean;
    };
  };
  role: 'C-suite' | 'SME' | 'Other'; // Add role field
  createdAt: Date;
  updatedAt: Date;
}

const sampleUser: User = {
  id: "user_123",
  name: "Jane Doe",
  email: "jane.doe@company.com",
  avatar: "https://example.com/avatar.jpg",
  preferences: {
    theme: "dark",
    language: "en",
    notificationPreferences: {
      email: true,
      inApp: false
    }
  },
  role: "C-suite", // or "SME"
  createdAt: new Date(),
  updatedAt: new Date()
};

interface User {
  id: string;
  name: string;
  email: string;
  avatar: string;
  preferences: {
    theme: 'dark' | 'light';
    language: 'en' | 'es' | 'fr';
    notificationPreferences: {
      email: boolean;
      inApp: boolean;
    };
  };
  role: 'C-suite' | 'SME' | 'Other'; // Add role field
  createdAt: Date;
  updatedAt: Date;
}

// Validation function to ensure role is one of the allowed values
function validateUserRole(user: User): boolean {
  const validRoles = ['C-suite', 'SME', 'Other'];
  return validRoles.includes(user.role);
}

// Sample user with C-suite/SME role
const sampleUser: User = {
  id: "user_123",
  name: "Jane Doe",
  email: "jane.doe@company.com",
  avatar: "https://example.com/avatar.jpg",
  preferences: {
    theme: "dark",
    language: "en",
    notificationPreferences: {
      email: true,
      inApp: false
    }
  },
  role: "C-suite", // Example: C-suite contact
  createdAt: new Date(),
  updatedAt: new Date()
};

// Validate the sample user
console.log("User role is valid:", validateUserRole(sampleUser)); // Should output: true

// EmailTemplate.ts
export interface EmailTemplate {
  id: string;
  template_name: string;
  subject: string;
  body: string;
  target_audience: 'C-suite' | 'SME' | 'Other';
  createdAt: Date;
  updatedAt: Date;
}

// Sample Email Templates for C-suite and SME
const emailTemplates: EmailTemplate[] = [
  {
    id: "template_001",
    template_name: "C-Suite Waste Valorization Outreach",
    subject: "Unlock Value from Your Waste Stream — A Strategic Opportunity",
    body: `
      Dear [First Name],

      I hope this message finds you well. I’m reaching out because your organization’s waste management practices present a significant opportunity for value creation — not just cost reduction, but revenue generation through advanced valorization technologies.

      Our team has developed a comprehensive 14-page report detailing how leading companies like yours are transforming waste into profit. The report includes case studies, ROI projections, and implementation frameworks tailored to your industry.

      Would you be open to a 15-minute call next week to explore how we can help you unlock hidden value in your waste stream?

      Best regards,
      [Your Name]
      [Your Title]
      [Your Company]
      [Contact Info]
    `,
    target_audience: 'C-suite',
    createdAt: new Date(),
    updatedAt: new Date()
  },
  {
    id: "template_002",
    template_name: "SME Waste Valorization Outreach",
    subject: "Turn Waste into Profit — No Matter Your Size",
    body: `
      Hi [First Name],

      I noticed your business is actively managing waste — and I wanted to share a simple, scalable solution that’s already helping SMEs like yours turn waste into revenue.

      Our 14-page report outlines practical steps to implement waste valorization with minimal upfront investment and maximum return. It’s designed for teams like yours — no heavy engineering, no complex contracts, just actionable insights.

      I’d love to send you the report and walk you through a few key strategies — no pressure, just value.

      Let me know if you’re open to a quick 10-minute chat next week.

      Thanks,
      [Your Name]
      [Your Title]
      [Your Company]
      [Contact Info]
    `,
    target_audience: 'SME',
    createdAt: new Date(),
    updatedAt: new Date()
  }
];

// Function to get template by audience
export function getTemplateByAudience(audience: 'C-suite' | 'SME' | 'Other'): EmailTemplate {
  const template = emailTemplates.find(t => t.target_audience === audience);
  if (!template) {
    throw new Error(`No template found for audience: ${audience}`);
  }
  return template;
}

// Validate template existence
export function validateTemplate(template: EmailTemplate): boolean {
  return (
    typeof template.id === 'string' &&
    typeof template.template_name === 'string' &&
    typeof template.subject === 'string' &&
    typeof template.body === 'string' &&
    ['C-suite', 'SME', 'Other'].includes(template.target_audience)
  );
}

// Example usage
console.log("C-suite template:", getTemplateByAudience('C-suite'));
console.log("SME template:", getTemplateByAudience('SME'));