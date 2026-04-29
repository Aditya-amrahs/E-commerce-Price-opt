import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Legend,
  Tooltip,
} from "chart.js";
import { Line } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Legend,
  Tooltip
);

const PriceChart = ({ data }: any) => {
  if (!data || data.length === 0) return <p>No data available</p>;

  const chartData = {
    labels: data.map((item: any) => item.product_id?.slice(0, 6)),
    datasets: [
      {
        label: "Our Price",
        data: data.map((item: any) => item.ourPrice),
        borderWidth: 2,
      },
      {
        label: "Competitor Price",
        data: data.map((item: any) => item.competitorPrice),
        borderWidth: 2,
      },
    ],
  };

  return <Line data={chartData} />;
};

export default PriceChart;