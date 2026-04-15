using System.Net;
using System.Net.Sockets;

namespace Emanon.E2E.Fixtures;

internal static class FreePort
{
    /// <summary>Grab a free loopback TCP port by opening and immediately closing a listener.</summary>
    public static int Pick()
    {
        var listener = new TcpListener(IPAddress.Loopback, 0);
        listener.Start();
        try
        {
            return ((IPEndPoint)listener.LocalEndpoint).Port;
        }
        finally
        {
            listener.Stop();
        }
    }
}
