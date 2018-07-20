import os
import pkgutil
import io


def get_example_data(filename):
    """Get a BytesIO object for a deloxfox example file.
    
    Parameters
    ----------
    filename : str
        Example file name to load.

    Returns
    -------
    BytesIO of the example file.
    """
    resource_str = os.path.join('example_data', filename)
    return io.BytesIO(pkgutil.get_data('bayfox', resource_str))
