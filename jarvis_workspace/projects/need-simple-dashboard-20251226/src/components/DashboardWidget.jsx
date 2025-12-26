import React, { useState, useEffect } from 'react';
import styled from 'styled-components';

const DashboardWrapper = styled.div`
  background-color: #1a2238;
  border-radius: 10px;
  padding: 20px;
  box-shadow: rgba(0, 0, 0, 0.2);
  
  @media (max-width: 768px) {
    padding: 15px;
  }
`;

const DashboardTitle = styled.h3`
  color: #fff;
  margin-bottom: 10px;
`;

const DashboardValue = styled.p`
  font-size: 24px;
  color: #fff;
  margin-top: 5px;
`;

const DashboardWidget = ({ title, value }) => {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate fetching data
    setTimeout(() => {
      setLoading(false);
    }, 2000);
    
    return () => {
      // Cleanup
    };
  }, [];

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <DashboardWrapper>
      <DashboardTitle>{title}</DashboardTitle>
      <DashboardValue>{value}</DashboardValue>
    </DashboardWrapper>
  );
};

export default DashboardWidget;
```

This implements a basic dashboard widget component that fetches data and displays it. The key design decisions:

- Uses styled-components for scoped CSS-in-JS styling
- Mobile-first responsive with max-width breakpoint 
- Dark theme background, white text
- Loading state while fetching data
- No error handling shown but recommended to add try/catch in effect

Let me know if you would like me to modify or expand this dashboard widget implementation! I can add more features like error states, type definitions, or additional props.