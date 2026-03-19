import React, { useEffect, useRef, useState } from 'react';
import cloudLayout from 'd3-cloud';
import { select } from 'd3';
import { scaleOrdinal } from 'd3-scale';
import { wordCloudAPI } from '../api/wordCloud';

interface WordCloudProps {
  onWordsSelected?: (words: string[]) => void;
}

interface Word {
  text: string;
  value: number;
}

export const WordCloud: React.FC<WordCloudProps> = ({ onWordsSelected }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [words, setWords] = useState<Word[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedWords, setSelectedWords] = useState<string[]>([]);

  const generateAndProcessWords = async () => {
    setIsLoading(true);
    try {
      const generatedWords = await wordCloudAPI.generateWords();
      const response = await wordCloudAPI.processWords(generatedWords);
      setWords(response.words);
      setSelectedWords(generatedWords);
      onWordsSelected?.(generatedWords);
    } catch (error) {
      console.error('Failed to generate word cloud:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (words.length === 0 || !svgRef.current) return;

    const width = 400;
    const height = 300;

    const layoutWords = words.map((d) => ({
      text: d.text,
      size: d.value * 20,
    }));

    const layout = cloudLayout()
      .size([width, height])
      .padding(5)
      .words(layoutWords)
      .random(() => 0.5)
      .on('end', (scaledWords) => {
        const svg = select(svgRef.current!);
        svg.selectAll('*').remove();

        const g = svg
          .append('g')
          .attr('transform', `translate(${width / 2},${height / 2})`);

        const colorScale = scaleOrdinal<string>()
          .domain(words.map((w) => w.text))
          .range([
            '#667eea',
            '#764ba2',
            '#f093fb',
            '#f5576c',
            '#4facfe',
            '#00f2fe',
            '#43e97b',
            '#38f9d7',
            '#fa709a',
            '#fee140',
          ]);

        const textSelection = g.selectAll('text')
          .data(scaledWords)
          .enter()
          .append('text')
          .attr('text-anchor', 'middle')
          .attr('transform', (d: any) => `translate(${d.x},${d.y}) rotate(${d.rotate})`)
          .attr('font-size', (d: any) => `${d.size}px`)
          .attr('font-family', 'sans-serif')
          .attr('fill', (d: any) => colorScale(d.text))
          .attr('cursor', 'pointer')
          .attr('user-select', 'none')
          .attr('opacity', 0);

        textSelection
          .transition()
          .duration(500)
          .attr('opacity', 1);

        textSelection.on('click', function(_: any, d: any) {
          const wordText = d.text;
          if (!wordText) return;
          const newSelected = selectedWords.includes(wordText)
            ? selectedWords.filter((w) => w !== wordText)
            : [...selectedWords, wordText];
          setSelectedWords(newSelected);
          onWordsSelected?.(newSelected);
        });
      });

    layout.start();

    return () => {
      layout.stop();
    };
  }, [words]);

  return (
    <div className="word-cloud-container">
      <div className="word-cloud-header">
        <h3>✨ 词云</h3>
        <button
          onClick={generateAndProcessWords}
          disabled={isLoading}
          className="generate-button"
        >
          {isLoading ? '生成中...' : '生成词云'}
        </button>
      </div>

      <div className="word-cloud-wrapper">
        <svg
          ref={svgRef}
          width={400}
          height={300}
          className="word-cloud-svg"
        />
      </div>

      {selectedWords.length > 0 && (
        <div className="selected-words">
          <p>已选词：{selectedWords.join(', ')}</p>
        </div>
      )}
    </div>
  );
};
