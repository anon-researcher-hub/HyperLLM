function analyze_degrees(hypergraph)
% ANALYZE_DEGREES Analyze node degree distribution
%
% Calculate and save node degree distribution, generate corresponding charts
%
% Parameters:
%   hypergraph - Hypergraph data structure

    fprintf('Analyzing degrees...\n');
    
    % Calculate degree of each node
    degree_list = [];
    node_keys = keys(hypergraph.node2edge);
    
    for i = 1:length(node_keys)
        node = node_keys{i};
        edge_indices = hypergraph.node2edge(node);
        if isscalar(edge_indices)
            degree = 1;
        else
            degree = length(edge_indices);
        end
        degree_list = [degree_list, double(degree)];
    end
    
    % Calculate degree distribution
    [degrees, ~, freq_idx] = unique(degree_list);
    freq = accumarray(freq_idx, 1);
    
    % Save results to file
    result_file = sprintf('results/%s_degrees.txt', hypergraph.datatype);
    fid = fopen(result_file, 'w');
    for i = 1:length(degrees)
        fprintf(fid, '%d %d\n', degrees(i), freq(i));
    end
    fclose(fid);
    
    % Start plotting from first non-zero degree
    if degrees(1) == 0
        start_idx = 2;
    else
        start_idx = 1;
    end
    
    if start_idx <= length(degrees)
        plot_loglog_analysis(degrees(start_idx:end), freq(start_idx:end), ...
                           'Degree', 'Count');
    end
    
    % Output statistics
    avg_degree = mean(degree_list);
    fprintf('The average degree of nodes: %.2f\n', avg_degree);
end 