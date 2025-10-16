export default function Dashboard() {
  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-gray-800">Dashboard</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* League Standing Card */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">League Standing</h3>
          <div className="text-4xl font-bold text-oracle-orange">-</div>
          <p className="text-gray-500 mt-2">Position in 10-team league</p>
        </div>
        
        {/* Current Week Card */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Current Week</h3>
          <div className="text-4xl font-bold text-oracle-blue">-</div>
          <p className="text-gray-500 mt-2">Categories winning</p>
        </div>
        
        {/* Acquisitions Card */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Weekly Acquisitions</h3>
          <div className="text-4xl font-bold text-green-600">- / 5</div>
          <p className="text-gray-500 mt-2">Moves remaining</p>
        </div>
      </div>
      
      {/* Quick Actions */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <button className="p-4 bg-oracle-orange text-white rounded-lg hover:bg-opacity-90 transition">
            View Recommendations
          </button>
          <button className="p-4 bg-oracle-blue text-white rounded-lg hover:bg-opacity-90 transition">
            Optimize Lineup
          </button>
          <button className="p-4 bg-green-600 text-white rounded-lg hover:bg-opacity-90 transition">
            Check Waiver Wire
          </button>
          <button className="p-4 bg-purple-600 text-white rounded-lg hover:bg-opacity-90 transition">
            Analyze Trade
          </button>
        </div>
      </div>
      
      {/* Recent Activity */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">Recent Activity</h3>
        <div className="text-gray-500 text-center py-8">
          Connect to Yahoo Fantasy to see your activity
        </div>
      </div>
    </div>
  )
}
