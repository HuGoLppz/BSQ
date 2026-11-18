/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   main.c                                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: marvin <marvin@42.fr>                      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/16 23:45:12 by marvin            #+#    #+#             */
/*   Updated: 2026/11/16 23:45:12 by marvin           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "bsq.h"

void	print_map_error(void)
{
	write(2, "map error\n", 10);
}

static void	write_all(char *str, long len)
{
	long	written;

	while (len > 0)
	{
		written = write(1, str, len);
		if (written <= 0)
			return ;
		str += written;
		len -= written;
	}
}

void	process_fd(int fd)
{
	t_map	map;

	if (!read_all(fd, &map))
	{
		print_map_error();
		return ;
	}
	if (parse_header(&map) && validate_map(&map) && solve(&map))
		write_all(map.grid, map.grid_len);
	else
		print_map_error();
	free(map.buf);
}

static void	process_file(char *path)
{
	int	fd;

	fd = open(path, O_RDONLY);
	if (fd < 0)
	{
		print_map_error();
		return ;
	}
	process_fd(fd);
	close(fd);
}

int	main(int argc, char **argv)
{
	int	i;

	if (argc < 2)
	{
		process_fd(0);
		return (0);
	}
	i = 1;
	while (i < argc)
	{
		if (i > 1)
			write(1, "\n", 1);
		process_file(argv[i]);
		i++;
	}
	return (0);
}
