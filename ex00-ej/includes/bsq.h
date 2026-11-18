/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   bsq.h                                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: marvin <marvin@42.fr>                      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/16 23:45:12 by marvin            #+#    #+#             */
/*   Updated: 2026/11/16 23:45:12 by marvin           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef BSQ_H
# define BSQ_H

# include <unistd.h>
# include <stdlib.h>
# include <fcntl.h>
# include <limits.h>

# define BUFFER_SIZE 65536

typedef struct s_map
{
	char	*buf;
	long	len;
	char	*grid;
	long	grid_len;
	int		rows;
	long	cols;
	char	empty;
	char	obstacle;
	char	full;
}	t_map;

typedef struct s_square
{
	int		size;
	int		row;
	long	col;
}	t_square;

void	print_map_error(void);
void	process_fd(int fd);
int		read_all(int fd, t_map *map);
int		parse_header(t_map *map);
int		validate_map(t_map *map);
int		solve(t_map *map);

#endif
