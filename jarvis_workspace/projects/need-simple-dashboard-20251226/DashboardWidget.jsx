import React from 'react';
import { useQuery } from '@apollo/client';
import { GET_CONNECTED_COMPANIES_COUNT_QUERY } from './queries';

const DashboardWidget = () => {
  const { data, loading, error } = useQuery(GET_CONNECTED_COMPANIES_COUNT_QUERY);

  if (error) {
    return <p>Error: {error.message}</p>;
  }

  return (
    <div className="dashboard-widget">
      <h3>Companies Connected This Week</h3>
      {loading && <p>Loading...</p>}
      {!loading && data && (
        <p>{data.connectedCompaniesCount} companies connected this week.</p>
      )}
    </div>
  );
};

export default DashboardWidget;