function analyze_hyperedge_sizes(hypergraph)

    fprintf('Analyzing hyperedge sizes...\n');
    
    % 计算每个超边的大小
    size_list = [];
    for i = 1:length(hypergraph.edges)
        edge_data = hypergraph.edges{i};
        nodes = edge_data{2};
        size_list = [size_list, double(length(nodes))];
    end
    
    [sizes, ~, freq_idx] = unique(size_list);
    freq = accumarray(freq_idx, 1);
    
    result_file = sprintf('results/%s_hyperedge_sizes.txt', hypergraph.datatype);
    fid = fopen(result_file, 'w');
    for i = 1:length(sizes)
        fprintf(fid, '%d %d\n', sizes(i), freq(i));
    end
    fclose(fid);
    
    plot_loglog_analysis(sizes, freq, ...
                       'Edge size', 'Count');
    
    avg_size = mean(size_list);
    fprintf('The average size of edges: %.2f\n', avg_size);
end 