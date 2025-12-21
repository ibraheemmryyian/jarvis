export interface Contact {
  id: string;
  name: string;
  email: string;
  phone: string;
  company: string;
  createdAt: string;
  updatedAt: string;
  notes?: Note[];
  deals?: Deal[];
}

export interface Deal {
  id: string;
  name: string;
  amount: number;
  stage: 'Prospecting' | 'Negotiation' | 'Closed Won' | 'Closed Lost';
  closeDate: string;
  contactId: string;
  createdAt: string;
  updatedAt: string;
  notes?: Note[];
}

export interface PipelineStage {
  id: string;
  name: string;
  color: string;
}

export interface Pipeline {
  id: string;
  name: string;
  stages: PipelineStage[];
  deals: Deal[];
}

export interface Note {
  id: string;
  content: string;
  createdAt: string;
  updatedAt: string;
  author: string;
  associatedWith: 'contact' | 'deal' | 'pipeline';
  associatedId: string;
}

export interface SearchQuery {
  searchTerm: string;
  filters: {
    type: 'contact' | 'deal' | 'note';
    stage?: string;
    dateRange?: {
      from: string;
      to: string;
    };
  };
}

export interface SearchResult {
  id: string;
  type: 'contact' | 'deal' | 'note';
  data: Contact | Deal | Note;
  score: number;
}

// src/models/Pipeline.ts
export interface Pipeline {
  id: string;
  name: string;
  stage_order: number;
  created_at: string;
}

// Simulated POST request to /api/search
const searchNotes = async (query: string, filters: { dateRange?: string; tag?: string }) => {
  // Mocked response based on query and filters
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

  // Apply filters
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