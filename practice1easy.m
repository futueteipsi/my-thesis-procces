clear; clc; close all;

% model parameters
grid_size = 80;
time_steps = 100;
density = 0.85;
initial_infected = 5;

threshold_infected = 2; 
recovery_time = 10;     

% initialization
grid = ones(grid_size, grid_size);

num_cells = grid_size * grid_size;
num_people = round(num_cells * density);
people_indices = randperm(num_cells, num_people);
grid(people_indices) = 0;

% матрица для отслеживания времени болезни каждой ячейки
infection_time = zeros(grid_size, grid_size);
margin = 3;

% случайные координаты X и Y
center_x = randi([margin + 1, grid_size - margin]);
center_y = randi([margin + 1, grid_size - margin]);

% заражаем группу 3x3 человека вокруг этой случайной точки
for dx = -1:1
    for dy = -1:1
        grid(center_x + dx, center_y + dy) = 2;        
        infection_time(center_x + dx, center_y + dy) = 1; 
    end
end


history_S = zeros(1, time_steps);
history_I = zeros(1, time_steps);
history_R = zeros(1, time_steps);

% visual
figure('Name', 'Epidemic modeling (Deterministic CA)', ...
       'Position', [100, 100, 1000, 450], 'NumberTitle', 'off');

custom_colormap = [
    0.0, 0.4, 0.8; ... 
    0.9, 0.9, 0.9; ... 
    0.8, 0.0, 0.0; ... 
    0.0, 0.6, 0.0      
];
colormap(custom_colormap);

% time
for t = 1:time_steps
    new_grid = grid;
    new_infection_time = infection_time;
    
    history_S(t) = sum(grid(:) == 0);
    history_I(t) = sum(grid(:) == 2);
    history_R(t) = sum(grid(:) == 3);

    subplot(1, 2, 1);
    imagesc(grid, [0 3]);
    axis square;
    title(sprintf('Cell space (day %d)', t));
    xlabel('X'); ylabel('Y');

    subplot(1, 2, 2);
    plot(1:t, history_S(1:t), 'b-', 'LineWidth', 1.5); hold on;
    plot(1:t, history_I(1:t), 'r-', 'LineWidth', 2.0);
    plot(1:t, history_R(1:t), 'g-', 'LineWidth', 1.5);
    hold off;
    grid on;
    title('Dynamics of SIR indicators');
    xlabel('Time (days)'); ylabel('People quantity');
    legend('S', 'I', 'R', 'Location', 'northeast');
    
    drawnow;

    if history_I(t) == 0
        fprintf('The epidemic over on the %d-th day.\n', t);
        history_S(t:end) = history_S(t);
        history_I(t:end) = 0;
        history_R(t:end) = history_R(t);
        break;
    end

    for i = 1:grid_size
        for j = 1:grid_size
            current_state = grid(i, j);
            
            % A: 0
            if current_state == 0
                num_infected_neighbors = 0;
                
                for di = -1:1
                    for dj = -1:1
                        if di == 0 && dj == 0, continue; end
                        
                        ni = i + di;
                        nj = j + dj;
                        
                        if ni >= 1 && ni <= grid_size && nj >= 1 && nj <= grid_size
                            if grid(ni, nj) == 2
                                num_infected_neighbors = num_infected_neighbors + 1;
                            end
                        end
                    end
                end

                if num_infected_neighbors >= threshold_infected
                    new_grid(i, j) = 2;
                    new_infection_time(i, j) = 1;
                end
                
            % B: 2
            elseif current_state == 2
                new_infection_time(i, j) = infection_time(i, j) + 1;

                if new_infection_time(i, j) > recovery_time
                    new_grid(i, j) = 3;           
                    new_infection_time(i, j) = 0; 
                end
            end
        end
    end
    
    grid = new_grid;
    infection_time = new_infection_time;
end
