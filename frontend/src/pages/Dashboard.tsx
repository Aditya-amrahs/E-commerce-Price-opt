import { useEffect, useState } from "react";
import Card from "../components/Card";
import PriceChart from "../components/PriceChart";

const Dashboard = () => {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/analysis")
      .then((res) => res.json())
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const totalProducts = data.length;

  const avgPrice =
    totalProducts > 0
      ? Math.round(
          data.reduce((sum, item) => sum + item.ourPrice, 0) / totalProducts
        )
      : 0;

  if (loading) return <div className="p-6">Loading dashboard...</div>;

  return (
    <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
      <Card title="Overview">
        <p>Total Products: {totalProducts}</p>
        <p>Avg Price: ₹{avgPrice.toLocaleString()}</p>
      </Card>

      <Card title="Price Comparison">
        <PriceChart data={data} />
      </Card>
    </div>
  );
};

export default Dashboard;