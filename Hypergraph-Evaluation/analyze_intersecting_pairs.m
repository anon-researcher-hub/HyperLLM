function analyze_intersecting_pairs(hypergraph)

    edges = hypergraph.edges;
    num_edges = length(edges);
    node2edge = hypergraph.node2edge;
    
    fprintf('📊 Dataset info: %d edges\n', num_edges);
    
    all_pairs_counts = [];
    intersecting_pairs_counts = [];
    cumulative_intersections = 0;
    
    num_time_points = min(20, num_edges);
    edges_per_point = floor(num_edges / num_time_points);
    
    fprintf('\n🔍 Starting incremental intersection analysis...\n');
    fprintf('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    
    for i = 1:num_edges
        intersecting_past_edges = containers.Map('KeyType', 'int32', 'ValueType', 'int32');
        current_edge_nodes = edges{i}{2};
        
        for node = current_edge_nodes
            if isKey(node2edge, node)
                past_edges = node2edge(node);
                for k = 1:length(past_edges)
                    past_edge_idx = past_edges(k);
                    if past_edge_idx < i
                        intersecting_past_edges(past_edge_idx) = 1;
                    end
                end
            end
        end
        
        new_intersections = length(keys(intersecting_past_edges));
        cumulative_intersections = cumulative_intersections + new_intersections;
        
        if mod(i, edges_per_point) == 0 || i == num_edges
            stage = floor(i / edges_per_point);
            total_possible_pairs = i * (i - 1) / 2;
            
            all_pairs_counts = [all_pairs_counts; total_possible_pairs];
            intersecting_pairs_counts = [intersecting_pairs_counts; cumulative_intersections];
            
            fprintf('📈 Stage %d/%d: Processed %d edges. Total intersections: %d\n', ...
                    stage, num_time_points, i, cumulative_intersections);
        end
    end
    
    fprintf('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    fprintf('🎯 Analysis completed! Processing results...\n');

    all_pairs_counts = double(all_pairs_counts);
    intersecting_pairs_counts = double(intersecting_pairs_counts);
    
    valid_idx = intersecting_pairs_counts > 0 & all_pairs_counts > 0;
    all_pairs_counts = all_pairs_counts(valid_idx);
    intersecting_pairs_counts = intersecting_pairs_counts(valid_idx);
    
    fprintf('📊 Valid data points for plot: %d\n', length(all_pairs_counts));
    
    if length(all_pairs_counts) >= 2
        fprintf('📈 Generating intersecting pairs visualization...\n');
        plot_loglog_analysis(all_pairs_counts, intersecting_pairs_counts, ...
                           '# of all pairs', '# of intersecting pairs');
        fprintf('✅ Intersecting pairs visualization complete!\n');
    else
        fprintf('❌ Warning: Not enough data points (%d) to generate plot.\n', length(all_pairs_counts));
    end
    
    fprintf('💾 Saving results...\n');
    if ~exist('results', 'dir')
        mkdir('results');
    end
    
    if ~isempty(all_pairs_counts)
        result_data = [all_pairs_counts, intersecting_pairs_counts];
        dlmwrite(sprintf('results/%s_intersecting_pairs.txt', hypergraph.datatype), result_data, 'delimiter', '\t');
        fprintf('✅ Results saved to: results/%s_intersecting_pairs.txt\n', hypergraph.datatype);
    end
    
end 