export default function Recommendations() {
  const categories = [
    { title: 'Top Waiver Wire Picks', count: 5, color: 'bg-green-600' },
    { title: 'Suggested Drops', count: 2, color: 'bg-red-600' },
    { title: 'Streaming Options', count: 8, color: 'bg-blue-600' },
    { title: 'Trade Targets', count: 3, color: 'bg-purple-600' },
  ]
  
  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-gray-800">Recommendations</h2>
      
      {/* Category Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {categories.map((cat) => (
          <div key={cat.title} className="bg-white p-6 rounded-lg shadow-md">
            <div className={`inline-block px-3 py-1 ${cat.color} text-white text-sm font-semibold rounded-full mb-3`}>
              {cat.count} available
            </div>
            <h3 className="text-lg font-semibold text-gray-800">{cat.title}</h3>
          </div>
        ))}
      </div>
      
      {/* Detailed Recommendations */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">
          Waiver Wire Recommendations
        </h3>
        <div className="text-gray-500 text-center py-8">
          Connect to Yahoo Fantasy to get personalized recommendations
        </div>
      </div>
    </div>
  )
}
