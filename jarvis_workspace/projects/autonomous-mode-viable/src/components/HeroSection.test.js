import React from 'react';
import { render, screen } from '@testing-library/react';
import { HeroSection } from './HeroSection';

describe('HeroSection', () => {
  test('renders correctly', () => {
    render(<HeroSection />);
    
    const title = screen.getByText(/Featured Products/i);
    expect(title).toBeInTheDocument();

    const productNames = screen.getAllByText(/Product Name/i);
    expect(productNames).toHaveLength(3);

    // Add more assertions as needed
  });

  test('loads data', () => {
    // Mock API response 
    jest.spyOn(axios, 'get').mockResolvedValue({ data: [{ id: 1, name: 'Product 1' }, { id: 2, name: 'Product 2' }] });
    
    render(<HeroSection />);
    
    expect(axios.get).toHaveBeenCalledWith('/api/herosection');

    // Verify loading state
    const loading = screen.getByText(/Loading/i);
    expect(loading).toBeInTheDocument();

    // Clean up mock
    axios.get.mockClear();
  });

  test('handles API error', () => {
    jest.spyOn(axios, 'get').mockRejectedValue(new Error('Network Error'));

    render(<HeroSection />);

    const error = screen.getByText(/Error/i);
    expect(error).toBeInTheDocument();

    // Verify no loading state
    const loading = screen.queryByText(/Loading/i);
    expect(loading).toBeNull();
  });
});

This sets up a complete HeroSection component with:

- Fetches featured products from an API 
- Displays loading/error states
- Uses styled-components for all styling
- Responsive design with CSS media queries
- Dark theme by default with gradient accents

The tests cover:
- Rendering of the title and product names
- Loading state when fetching data
- Handling of API errors 

Let me know if you have any other questions!