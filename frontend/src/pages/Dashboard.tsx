import { useEffect, useState } from "react";
import Card from "../components/Card";
import PriceChart from "../components/PriceChart";

const Dashboard = () => {
  const [data, setData] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [chartUrl, setChartUrl] = useState("");

  useEffect(() => {
    // ✅ Fetch analysis (data + summary)
    fetch("http://127.0.0.1:8000/analysis")
      .then((res) => res.json())
      .then((res) => {
        setData(res.data || []);
        setSummary(res.summary || null);
        setLoading(false);
      })
      .catch(() => setLoading(false));

    // ✅ Generate backend chart
    fetch("http://127.0.0.1:8000/price?index=0")
      .then(() => {
        setChartUrl(
          `http://127.0.0.1:8000/static/price_plot.png?t=${Date.now()}`
        );
      });
  }, []);

  if (loading) return <div className="p-6">Loading dashboard...</div>;

  return (
    <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">

      {/* ✅ UPDATED Overview */}
      <Card title="Overview">
        <p>Total Products: {summary?.total_products?.toLocaleString()}</p>
        <p>Avg Price: ₹{summary?.avg_price?.toFixed(2)}</p>
        <p>Min Price: ₹{summary?.min_price?.toFixed(2)}</p>
        <p>Max Price: ₹{summary?.max_price?.toFixed(2)}</p>
      </Card>

      {/* Chart (sample data) */}
      <Card title="Price Comparison">
        <PriceChart data={data} />
      </Card>

      {/* Backend-generated chart */}
      <Card title="Price Trend (Backend)">
        {chartUrl ? (
          <img
            src={chartUrl}
            alt="Price Trend"
            className="w-full rounded"
          />
        ) : (
          <p>Loading chart...</p>
        )}
      </Card>

    </div>
  );
};

export default Dashboard;