#include "header.h"

static void	print_file(char *path)
{
	int	fd;

	fd = open(path, O_RDONLY);
	if (fd < 0)
	{
		write(2, "map error\n", 10);
		return ;
	}
	if (!print_map(fd))
		write(2, "map error\n", 10);
	close(fd);
}

int	main(int argc, char **argv)
{
	int	i;

	if (argc < 2)
	{
		if (!print_map(0))
			write(2, "map error\n", 10);
		return (0);
	}
	i = 1;
	while (i < argc)
	{
		if (i > 1)
			write(1, "\n", 1);
		print_file(argv[i]);
		i++;
	}
	return (0);
}
