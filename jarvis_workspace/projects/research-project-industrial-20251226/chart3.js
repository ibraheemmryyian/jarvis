// Code to generate a line chart showing the trend of material flow efficiency scores over time for an industry
import { Line } from 'react-chartjs-2';
import { Chart, CategoryScale, LinearScale, PointElement, LineElement } from 'chart.js';

Chart.register(CategoryScale, LinearScale, PointElement, LineElement);

const data = {
  labels: ['2019', '2020', '2021', '2022'],
  datasets: [
    {
      label: 'Material Flow Efficiency Score',
      data: [75, 80, 85, 90],
      fill: false,
      borderColor: '#4caf50',
      tension: 0.4,
    },
  ],
};

const options = {
  elements: {
    point: {
      radius: 0,
    },
  },
};

return (
  <div>
    <Line data={data} options={options} />
  </div>
);