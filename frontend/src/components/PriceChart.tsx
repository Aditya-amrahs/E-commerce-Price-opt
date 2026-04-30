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

        // ✅ BLUE LINE
        borderColor: "#2563eb",
        backgroundColor: "rgba(37, 99, 235, 0.2)",
        borderWidth: 3,
        tension: 0.4,
        pointRadius: 3,
      },
      {
        label: "Competitor Price",
        data: data.map((item: any) => item.competitorPrice),

        // ✅ RED LINE
        borderColor: "#dc2626",
        backgroundColor: "rgba(220, 38, 38, 0.2)",
        borderWidth: 3,
        tension: 0.4,
        pointRadius: 3,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: "top" as const,
      },
      tooltip: {
        mode: "index" as const,
        intersect: false,
      },
    },
    interaction: {
      mode: "nearest" as const,
      axis: "x" as const,
      intersect: false,
    },
  };

  return <Line data={chartData} options={options} />;
};

export default PriceChart;