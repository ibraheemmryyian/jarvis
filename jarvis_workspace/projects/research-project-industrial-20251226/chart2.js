// Code to generate a pie chart showing the distribution of material flow types (diversion, valorization, incineration, landfill) for an industry
import { Pie } from 'react-chartjs-2';
import { Chart, CategoryScale, LinearScale, PieElement, ArcElement } from 'chart.js';

Chart.register(CategoryScale, LinearScale, PieElement, ArcElement);

const data = {
  labels: ['Diversion', 'Valorization', 'Incineration', 'Landfill'],
  datasets: [
    {
      label: '# of Material Flows',
      data: [50, 30, 10, 10],
      backgroundColor: ['#4caf50', '#f44336', '#2196f3', '#e91e63'],
    },
  ],
};

return (
  <div>
    <Pie data={data} />
  </div>
);