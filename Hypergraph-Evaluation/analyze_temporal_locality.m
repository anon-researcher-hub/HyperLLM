function analyze_temporal_locality(hypergraph)

    fprintf('Analyzing temporal locality...\n');
    
    edges = hypergraph.edges;
    num_edges = length(edges);
    
    fprintf('📊 Dataset info: %d edges\n', num_edges);
    
    temporal_similarities = [];
    time_gaps = [];
    
    start_edge = max(1, num_edges - 1000);
    edges_to_analyze = num_edges - start_edge + 1;
    
    fprintf('🔄 Analysis scope: Last %d edges\n', edges_to_analyze);
    fprintf('\n🔍 Computing temporal similarities...\n');
    fprintf('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    
    for i = start_edge:num_edges
        if mod(i - start_edge + 1, 100) == 0
            fprintf('📈 Progress: %.0f%%\n', 100 * (i - start_edge + 1) / edges_to_analyze);
        end
        
        current_edge_nodes = edges{i}{2};
        
        for gap = 1:min(20, i-1)
            if i - gap >= 1
                prev_edge_nodes = edges{i - gap}{2};
                
                intersection_size = length(intersect(current_edge_nodes, prev_edge_nodes));
                union_size = length(union(current_edge_nodes, prev_edge_nodes));
                
                if union_size > 0
                    similarity = intersection_size / union_size;
                    temporal_similarities = [temporal_similarities; similarity];
                    time_gaps = [time_gaps; gap];
                end
            end
        end
    end
    
    fprintf('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    
    if ~isempty(time_gaps)
        unique_gaps = unique(time_gaps);
        avg_similarities = zeros(size(unique_gaps));
        
        for i = 1:length(unique_gaps)
            avg_similarities(i) = mean(temporal_similarities(time_gaps == unique_gaps(i)));
        end
        
        if length(unique_gaps) >= 2
            figure('Position', [100, 100, 800, 600]);
            plot(unique_gaps, avg_similarities, 'o', 'MarkerSize', 12, ...
                 'MarkerFaceColor', [0.5, 0.2, 0.8], 'MarkerEdgeColor', [0.5, 0.2, 0.8], ...
                 'LineWidth', 1.5);
                 
            xlabel('Time gap', 'FontSize', 60, 'FontWeight', 'bold', 'Interpreter', 'none');
            ylabel('Average similarity', 'FontSize', 60, 'FontWeight', 'bold', 'Interpreter', 'none');
            
            grid off;
            box off;
            
            set(gca, 'FontSize', 56, 'FontWeight', 'bold');
            set(gca, 'LineWidth', 2);
            
            set(gca, 'XMinorTick', 'off', 'YMinorTick', 'off');
            
            set(gca, 'XColor', 'black', 'YColor', 'black');
            set(gca, 'TickLength', [0.02, 0.02]);
            

        else
             fprintf('⚠️  Insufficient data for plot.\n');
        end
        
        if exist('results', 'dir') ~= 7
            mkdir('results');
        end
        result_data = [unique_gaps, avg_similarities];
        dlmwrite(sprintf('results/%s_temporal_locality.txt', hypergraph.datatype), result_data, 'delimiter', '\t');
    end
    
end 