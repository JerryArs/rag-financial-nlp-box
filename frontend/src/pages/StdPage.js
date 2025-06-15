import React, { useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { TextInput } from '../components/shared/ModelOptions';

const StdPage = () => {
  const [input, setInput] = useState('');
  const [result, setResult] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [termTypes, setTermTypes] = useState({
    allFinancialTerms: false,
  });

  const handleTermTypeChange = (e) => {
    const { name, checked } = e.target;
    setTermTypes({ [name]: checked });
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/std', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: input, termTypes }),
      });
      const data = await response.json();
      setResult(JSON.stringify(data, null, 2));
    } catch (error) {
      console.error('Error:', error);
      setResult('An error occurred while processing the request.');
    }
    setIsLoading(false);
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">金融术语标准化 💰</h1>
      <div className="bg-white shadow-md rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">输入金融文本</h2>
        <TextInput
          value={input}
          onChange={(e) => setInput(e.target.value)}
          rows={4}
          placeholder="请输入需要进行术语标准化的金融文本..."
        />
        
        <div className="bg-white shadow-md rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">术语类型</h2>
          <div className="space-y-3">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="allFinancialTerms"
                name="allFinancialTerms"
                checked={termTypes.allFinancialTerms}
                onChange={handleTermTypeChange}
                className="mr-2"
              />
              <label htmlFor="allFinancialTerms" className="font-semibold">所有金融术语</label>
            </div>
          </div>
        </div>

        <button
          onClick={handleSubmit}
          disabled={isLoading}
          className={`bg-green-500 text-white px-4 py-2 rounded-md hover:bg-green-600 ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          {isLoading ? '处理中...' : '标准化术语'}
        </button>
      </div>
      {result && (
        <div className="bg-green-100 border-l-4 border-green-500 text-green-700 p-4 mb-6" role="alert">
          <p className="font-bold">标准化结果：</p>
          <pre>{result}</pre>
        </div>
      )}
      <div className="flex items-center text-yellow-700 bg-yellow-100 p-4 rounded-md">
        <AlertCircle className="mr-2" />
        <span>这是演示版本, 并非所有功能都可以正常工作。更多功能需要您来增强并实现。</span>
      </div>
    </div>
  );
};

export default StdPage;