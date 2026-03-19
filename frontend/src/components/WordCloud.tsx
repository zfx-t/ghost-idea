import React, { useEffect, useState, useCallback } from 'react';
import cloudLayout from 'd3-cloud';
import { select } from 'd3';
import { scaleOrdinal } from 'd3-scale';
import { wordCloudAPI } from '../api/wordCloud';
import { X } from 'lucide-react';

interface WordCloudProps {
  onWordsSelected?: (words: string[]) => void;
}

interface Word {
  text: string;
  value: number;
}

export const WordCloud: React.FC<WordCloudProps> = ({ onWordsSelected }) => {
  const [words, setWords] = useState<Word[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedWords, setSelectedWords] = useState<string[]>([]);

  const generateAndProcessWords = useCallback(async () => {
    setIsLoading(true);
    try {
      const generatedWords = await wordCloudAPI.generateWords();
      const response = await wordCloudAPI.processWords(generatedWords);
      setWords(response.words);
      setSelectedWords([]);
      onWordsSelected?.([]);
    } catch (error) {
      console.error('Failed to generate word cloud:', error);
    } finally {
      setIsLoading(false);
    }
  }, [onWordsSelected]);

  useEffect(() => {
    if (words.length === 0) return;
    
    const width = 260;
    const height = 180;
    
    const svgEl = document.querySelector('.word-cloud-svg') as SVGSVGElement;
    if (!svgEl) return;

    const fontSizeScale = [28, 22, 18];
    const layoutWords = words.map((d, i) => ({
      text: d.text,
      size: fontSizeScale[i % fontSizeScale.length],
    }));

    const svg = select(svgEl);
    svg.selectAll('*').remove();

    const g = svg.append('g')
      .attr('transform', `translate(${width / 2},${height / 2})`);

    const colorScale = scaleOrdinal<string>()
      .domain(words.map((w) => w.text))
      .range(['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe', '#43e97b', '#38f9d7', '#fa709a', '#fee140']);

    const layout = cloudLayout()
      .size([width, height])
      .padding(10)
      .words(layoutWords)
      .spiral('archimedean')
      .rotate(0);

    layout.start();

    const timer = setInterval(() => {
      const currentWords = layout.words();
      if (currentWords.length > 0 && currentWords[0].x !== undefined) {
        clearInterval(timer);
        
        g.selectAll('text')
          .data(currentWords)
          .enter()
          .append('text')
          .attr('text-anchor', 'middle')
          .attr('transform', (d: any) => `translate(${d.x},${d.y})`)
          .attr('font-size', (d: any) => `${d.size}px`)
          .attr('font-family', 'sans-serif')
          .attr('fill', (d: any) => colorScale(d.text))
          .attr('cursor', 'pointer')
          .attr('class', 'word-cloud-text')
          .attr('opacity', '1')
          .on('click', function(this: any, _: any, d: any) {
            const wordText = d.text;
            const isSelected = selectedWords.includes(wordText);
            const newSelected = isSelected 
              ? selectedWords.filter(w => w !== wordText)
              : [...selectedWords, wordText];
            setSelectedWords(newSelected);
            onWordsSelected?.(newSelected);
            select(this).classed('selected', !isSelected);
          });
        
        layout.stop();
      }
    }, 50);

    return () => {
      clearInterval(timer);
      layout.stop();
    };
  }, [words]);

  const removeSelectedWord = (word: string) => {
    const newSelected = selectedWords.filter(w => w !== word);
    setSelectedWords(newSelected);
    onWordsSelected?.(newSelected);
  };

  return (
    <div className="word-cloud-container">
      <div className="word-cloud-header">
        <h3>✨ 词云</h3>
        <button onClick={generateAndProcessWords} disabled={isLoading} className="generate-button">
          {isLoading ? '生成中...' : '🔄 换一批'}
        </button>
      </div>

      <div className="word-cloud-wrapper">
        <svg className="word-cloud-svg" width="260" height="180" />
      </div>

      <div className="selected-words">
        <p>已选词条：</p>
        {selectedWords.length > 0 ? (
          <div className="selected-tags">
            {selectedWords.map((word) => (
              <span key={word} className="selected-tag">
                {word}
                <button onClick={() => removeSelectedWord(word)} className="remove-tag" title="取消选择">
                  <X size={14} />
                </button>
              </span>
            ))}
          </div>
        ) : (
          <p className="no-selection">点击词云中的词语进行选择</p>
        )}
      </div>
    </div>
  );
};
