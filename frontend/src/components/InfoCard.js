// src/components/InfoCard.js
import React, { useState } from 'react';
import './InfoCard.css';

const termDefinitions = {
  'Sharpe Ratio': 'Risk başına düşen getiri oranı. Ne kadar yüksekse o kadar iyi.',
  'Volatility': 'Hisse fiyatının oynaklığı, fiyatın ne kadar dalgalandığını gösterir.',
  'Max Drawdown': 'Bir yatırımın en yüksekten en düşük seviyeye düşüşünü gösterir.',
  'P/E Ratio': 'Fiyat/Kazanç oranı, hisse fiyatının kazançlara oranı.',
  'Beta': 'Hissenin piyasa ile korelasyonu, 1\'den büyükse piyasadan daha volatil demektir.',
  'Alpha': 'Yatırımın piyasaya göre ekstra getiri sağlama kapasitesi.',
  'ROE': 'Özkaynak kârlılığı, şirketin özkaynak kullanımı ile ne kadar kazandığını gösterir.',
  'ROA': 'Aktif kârlılığı, toplam varlıklar üzerinden elde edilen kâr oranı.',
  'Debt/Equity': 'Borç/Özkaynak oranı, şirketin finansal riskini gösterir.',
  'Forward P/E': 'Gelecek kazançlara göre fiyat/kazanç oranı.',
  'PEG Ratio': 'Fiyat/Kazanç-Oran büyüme oranı, şirketin değerini büyüme ile ilişkilendirir.',
  'Current Ratio': 'Cari oran, şirketin kısa vadeli borçlarını karşılama kapasitesi.',
  'Quick Ratio': 'Asit-test oranı, nakit ve kısa vadeli alacaklarla borçları karşılama yeteneği.',
  'VaR': 'Value at Risk, belirli bir güven aralığında olası maksimum kayıp.',
  'CVaR': 'Expected Shortfall, VaR’ı aşan durumlarda ortalama kayıp.',
};

const InfoCard = () => {
  const [expanded, setExpanded] = useState(false);
  
  const toggleCard = () => setExpanded(prev => !prev);

  return (
    <div 
      className={`info-card ${expanded ? 'expanded' : 'collapsed'}`}
      onClick={toggleCard}
    >
      <div className="info-card-header">
        <span>ℹ️ Info</span>
      </div>
      
      {expanded && (
        <div className="info-card-content">
          {Object.entries(termDefinitions).map(([term, definition]) => (
            <p key={term}>
              <strong>{term}:</strong> {definition}
            </p>
          ))}
        </div>
      )}
    </div>
  );
};

export default InfoCard;
