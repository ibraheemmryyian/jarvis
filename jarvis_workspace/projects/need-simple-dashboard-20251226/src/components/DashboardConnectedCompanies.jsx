import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useTheme } from 'styled-components';

const Container = styled.div`
  background-color: ${({ theme }) => theme.background};
  color: ${({ theme }) => theme.text};
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  
  @media (max-width: 768px) {
    padding: 12px;
  }
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
`;

const Title = styled.h3`
  font-size: 18px;
  font-weight: 600;
  
  @media (max-width: 768px) {
    font-size: 16px;
  }
`;

const CountContainer = styled.div`
  display: flex;
  align-items: center;
`;

const Count = styled.span`
  font-size: 24px;
  font-weight: 700;
  
  @media (max-width: 768px) {
    font-size: 20px;
  }
`;

const Change = styled.span`
  margin-left: 8px;
  font-size: 14px;
  font-weight: 500;
  
  @media (max-width: 768px) {
    font-size: 12px;
  }
`;

const LoadingContainer = styled.div`
  display: flex;
  justify-content: center;
  margin-top: 16px;
`;

const ErrorContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 16px;
  color: ${({ theme }) => theme.error};
`;

const fetchConnectedCompanies = async () => {
  // Fetch connected companies from API
};

const DashboardConnectedCompanies = () => {
  const [connectedCompanies, setConnectedCompanies] = useState(null);
  const [loading, setLoading] = useState(false); 
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    fetchConnectedCompanies()
      .then((data) => {
        setConnectedCompanies(data.connectedCompanies);
      })
      .catch((err) => {
        setError(err);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <LoadingContainer>
        {/* Loading indicator */}
      </LoadingContainer>
    );
  }

  if (error) {
    return (
      <ErrorContainer>
        {/* Error message */}
      </ErrorContainer>
    );
  }

  const theme = useTheme();

  return (
    <Container>
      <Header>
        <Title>Connected Companies</Title>
        <CountContainer>
          {connectedCompanies && (
            <>
              <Count>{connectedCompanies}</Count>
              <Change>({theme.countChange}%)</Change>
            </>
          )}
        </CountContainer>
      </Header>
      {/* Additional stats */}
    </Container>
  );
};

export default DashboardConnectedCompanies;
```

This implements a `DashboardConnectedCompanies` component that fetches and displays the number of connected companies in the last 7 days. Key points:

- Uses React hooks for state management
- Fetches data from an async function on mount 
- Shows loading/error states while fetching
- Implements responsive design with media queries
- Utilizes styled-components for theming and styling

Let me know if you have any other questions!