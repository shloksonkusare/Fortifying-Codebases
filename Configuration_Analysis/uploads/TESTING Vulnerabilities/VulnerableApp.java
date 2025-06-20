import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.Statement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.io.IOException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public class VulnerableApp {

    // SQL Injection Vulnerability
    public void vulnerableSqlMethod(String userInput) {
        try {
            Connection conn = DriverManager.getConnection("jdbc:mysql://localhost:3306/mydb", "user", "password");
            Statement stmt = conn.createStatement();
            String query = "SELECT * FROM users WHERE username = '" + userInput + "'";
            ResultSet rs = stmt.executeQuery(query);

            while (rs.next()) {
                System.out.println("User ID: " + rs.getInt("id"));
            }

            rs.close();
            stmt.close();
            conn.close();
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    // Cross-Site Scripting (XSS) Vulnerability
    public void vulnerableXssMethod(HttpServletRequest request, HttpServletResponse response) throws IOException {
        String userInput = request.getParameter("userInput");
        response.getWriter().println("<html><body>User input: " + userInput + "</body></html>");
    }

    // Command Injection Vulnerability
    public void vulnerableCommandMethod(String userInput) {
        try {
            Runtime.getRuntime().exec("cmd /c " + userInput);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    // Insecure Deserialization Vulnerability
    public void vulnerableDeserializationMethod(byte[] serializedObject) {
        try {
            ObjectInputStream in = new ObjectInputStream(new ByteArrayInputStream(serializedObject));
            Object obj = in.readObject();
            in.close();
        } catch (IOException | ClassNotFoundException e) {
            e.printStackTrace();
        }
    }

    // Path Traversal Vulnerability
    public void vulnerablePathTraversalMethod(HttpServletRequest request) throws IOException {
        String filename = request.getParameter("filename");
        File file = new File("/var/www/uploads/" + filename);
        FileInputStream fis = new FileInputStream(file);
        // Process the file...
        fis.close();
    }
    
    // Integer Overflow Vulnerability
    public void vulnerableIntegerOverflowMethod(int number) {
        int result = number * 1000;
        System.out.println("Result: " + result);
    }

    // Buffer Overflow Vulnerability
    public void vulnerableBufferOverflowMethod() {
        byte[] buffer = new byte[10];
        for (int i = 0; i < 20; i++) {
            buffer[i] = (byte) i;
        }
        System.out.println("Buffer overflow occurred");
    }

    // XML External Entity (XXE) Vulnerability
    public void vulnerableXXEMethod(String xmlInput) {
        try {
            DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
            dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", false);
            DocumentBuilder db = dbf.newDocumentBuilder();
            Document doc = db.parse(new InputSource(new StringReader(xmlInput)));
            // Process the document...
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
