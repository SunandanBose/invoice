import { useState } from "react";
import { Plus, Trash2, FileText, Calendar, User, Package, Loader2 } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";

interface LineItem {
  id: string;
  name: string;
  quantity: string;
  rate: string;
}

// API Configuration
const API_ENDPOINT = "https://makvdn2awf.execute-api.us-east-1.amazonaws.com/default/invoice-generator";
const API_KEY = ""; // Add your API key here if using API key authentication

export const InvoiceForm = () => {
  const [invoiceNumber, setInvoiceNumber] = useState("");
  const [recipientName, setRecipientName] = useState("");
  const [recipientAddress, setRecipientAddress] = useState("");
  const [recipientGst, setRecipientGst] = useState("");
  const [invoiceDate, setInvoiceDate] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [items, setItems] = useState<LineItem[]>([
    { id: "1", name: "", quantity: "", rate: "" }
  ]);
  const [isGenerating, setIsGenerating] = useState(false);
  const { toast } = useToast();

  const addItem = () => {
    setItems([
      ...items,
      { id: Date.now().toString(), name: "", quantity: "", rate: "" }
    ]);
  };

  const removeItem = (id: string) => {
    if (items.length > 1) {
      setItems(items.filter(item => item.id !== id));
    }
  };

  const updateItem = (id: string, field: keyof LineItem, value: string) => {
    setItems(items.map(item => 
      item.id === id ? { ...item, [field]: value } : item
    ));
  };

  const calculateItemTotal = (item: LineItem) => {
    const qty = parseFloat(item.quantity) || 0;
    const rate = parseFloat(item.rate) || 0;
    return qty * rate;
  };

  const calculateSubtotal = () => {
    return items.reduce((sum, item) => sum + calculateItemTotal(item), 0);
  };

  const subtotal = calculateSubtotal();
  const cgst = subtotal * 0.09;
  const sgst = subtotal * 0.09;
  const total = subtotal + cgst + sgst;

  const formatDate = (dateString: string) => {
    if (!dateString) return "";
    const date = new Date(dateString);
    const day = date.getDate();
    const month = date.toLocaleString('en-US', { month: 'short' });
    const year = date.getFullYear();
    return `${day.toString().padStart(2, '0')}-${month}-${year}`;
  };

  const generateInvoice = async () => {
    // Validation
    if (!invoiceNumber) {
      toast({
        title: "Missing Information",
        description: "Please enter an invoice number",
        variant: "destructive"
      });
      return;
    }
    
    if (!invoiceDate) {
      toast({
        title: "Missing Information",
        description: "Please select an invoice date",
        variant: "destructive"
      });
      return;
    }

    if (!recipientName) {
      toast({
        title: "Missing Information",
        description: "Please enter recipient name",
        variant: "destructive"
      });
      return;
    }

    if (items.length === 0 || !items[0].name) {
      toast({
        title: "Missing Information",
        description: "Please add at least one item",
        variant: "destructive"
      });
      return;
    }

    setIsGenerating(true);

    try {
      // Combine recipient fields into the format expected by backend
      const recipientParts = [];
      if (recipientName) recipientParts.push(recipientName);
      if (recipientAddress) recipientParts.push(recipientAddress);
      if (recipientGst) recipientParts.push(`GST NO: ${recipientGst}`);
      const recipient = recipientParts.join('\n');

      // Prepare invoice data
      const invoiceData = {
        invoice_no: invoiceNumber,
        invoice_date: formatDate(invoiceDate),
        to: recipient,
        job_description: jobDescription || "",
        items: items.map(item => ({
          name: item.name,
          hsn: "997329", // Default HSN code
          qty: parseInt(item.quantity) || 0,
          rate: item.rate,
          amount: calculateItemTotal(item).toString()
        })),
        taxable_amount: subtotal.toString(),
        cgst: cgst.toFixed(2),
        sgst: sgst.toFixed(2),
        total: total.toFixed(2)
      };

      // Prepare headers
      const headers: Record<string, string> = {
        "Content-Type": "application/json"
      };

      // Add API key if configured
      if (API_KEY) {
        headers["x-api-key"] = API_KEY;
      }

      // Call API
      const response = await fetch(API_ENDPOINT, {
        method: "POST",
        headers: headers,
        body: JSON.stringify(invoiceData)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API Error: ${response.status} - ${errorText}`);
      }

      // Check if response is PDF or JSON
      const contentType = response.headers.get("content-type");
      let blob: Blob;

      if (contentType && contentType.includes("application/pdf")) {
        // Direct PDF response
        blob = await response.blob();
      } else {
        // JSON response with base64 encoded PDF
        const result = await response.json();
        const base64Data = result.body;
        const binaryString = atob(base64Data);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
          bytes[i] = binaryString.charCodeAt(i);
        }
        blob = new Blob([bytes], { type: "application/pdf" });
      }
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `invoice_${invoiceNumber}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      toast({
        title: "Success!",
        description: `Invoice ${invoiceNumber} has been downloaded`,
      });

    } catch (error) {
      console.error("Error generating invoice:", error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to generate invoice. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="min-h-screen bg-background pb-24">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-background/80 backdrop-blur-lg border-b border-border px-4 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-foreground">New Invoice</h1>
          {/* Preview button hidden as requested */}
        </div>
      </header>

      <div className="px-4 py-6 space-y-6">
        {/* Invoice Details Section */}
        <section className="space-y-4">
          <div className="flex items-center gap-2 text-foreground">
            <FileText className="w-5 h-5 text-primary" />
            <h2 className="font-semibold">Invoice Details</h2>
          </div>
          
          <div className="bg-card rounded-2xl p-4 shadow-soft space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <Input 
                label="Invoice No."
                placeholder="INV-001"
                value={invoiceNumber}
                onChange={(e) => setInvoiceNumber(e.target.value)}
              />
              <Input 
                label="Date"
                type="date"
                value={invoiceDate}
                onChange={(e) => setInvoiceDate(e.target.value)}
              />
            </div>
          </div>
        </section>

        {/* Recipient Section */}
        <section className="space-y-4">
          <div className="flex items-center gap-2 text-foreground">
            <User className="w-5 h-5 text-primary" />
            <h2 className="font-semibold">Bill To</h2>
          </div>
          
          <div className="bg-card rounded-2xl p-4 shadow-soft space-y-4">
            <Input 
              label="Recipient Name"
              placeholder="Enter recipient name..."
              value={recipientName}
              onChange={(e) => setRecipientName(e.target.value)}
            />
            <Textarea 
              label="Recipient Address"
              placeholder="Enter recipient address..."
              value={recipientAddress}
              onChange={(e) => setRecipientAddress(e.target.value)}
              className="min-h-[60px]"
            />
            <Input 
              label="Recipient GST No"
              placeholder="Enter GST number (e.g., 20RCHS01462GIDA)"
              value={recipientGst}
              onChange={(e) => setRecipientGst(e.target.value)}
            />
          </div>
        </section>

        {/* Job Description Section */}
        <section className="space-y-4">
          <div className="flex items-center gap-2 text-foreground">
            <Calendar className="w-5 h-5 text-primary" />
            <h2 className="font-semibold">Job Description</h2>
          </div>
          
          <div className="bg-card rounded-2xl p-4 shadow-soft">
            <Textarea 
              placeholder="Describe the work or services..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              className="min-h-[80px]"
            />
          </div>
        </section>

        {/* Line Items Section */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-foreground">
              <Package className="w-5 h-5 text-primary" />
              <h2 className="font-semibold">Items</h2>
            </div>
            <span className="text-sm text-muted-foreground">{items.length} item{items.length !== 1 ? 's' : ''}</span>
          </div>
          
          <div className="space-y-3">
            {items.map((item, index) => (
              <div 
                key={item.id} 
                className="bg-card rounded-2xl p-4 shadow-soft space-y-3 relative overflow-hidden"
              >
                <div className="absolute top-0 left-0 w-1 h-full bg-primary rounded-l-2xl" />
                
                <div className="flex items-start justify-between gap-2">
                  <span className="text-xs font-medium text-muted-foreground bg-secondary px-2 py-1 rounded-full">
                    Item {index + 1}
                  </span>
                  {items.length > 1 && (
                    <button 
                      onClick={() => removeItem(item.id)}
                      className="text-destructive/70 hover:text-destructive transition-colors p-1"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>

                <Input 
                  placeholder="Item name or description"
                  value={item.name}
                  onChange={(e) => updateItem(item.id, "name", e.target.value)}
                />

                <div className="grid grid-cols-2 gap-3">
                  <Input 
                    type="number"
                    placeholder="Qty"
                    value={item.quantity}
                    onChange={(e) => updateItem(item.id, "quantity", e.target.value)}
                  />
                  <Input 
                    type="number"
                    placeholder="Rate (₹)"
                    value={item.rate}
                    onChange={(e) => updateItem(item.id, "rate", e.target.value)}
                  />
                </div>

                {(item.quantity && item.rate) && (
                  <div className="flex justify-end pt-2 border-t border-border">
                    <span className="text-sm font-semibold text-foreground">
                      ₹ {calculateItemTotal(item).toLocaleString('en-IN')}
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>

          <button 
            onClick={addItem}
            className="w-full py-3 border-2 border-dashed border-primary/30 rounded-2xl text-primary font-medium flex items-center justify-center gap-2 hover:bg-primary/5 transition-colors"
          >
            <Plus className="w-5 h-5" />
            Add Item
          </button>
        </section>

        {/* Summary Section */}
        <section className="bg-card rounded-2xl p-4 shadow-medium space-y-3">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Subtotal</span>
            <span className="font-medium">₹ {subtotal.toLocaleString('en-IN')}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">CGST (9%)</span>
            <span className="font-medium">₹ {cgst.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">SGST (9%)</span>
            <span className="font-medium">₹ {sgst.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</span>
          </div>
          <div className="border-t border-border pt-3 flex justify-between">
            <span className="font-semibold text-foreground">Total</span>
            <span className="text-xl font-bold text-primary">₹ {total.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</span>
          </div>
        </section>
      </div>

      {/* Fixed Bottom Button */}
      <div className="fixed bottom-0 left-0 right-0 p-4 bg-background/80 backdrop-blur-lg border-t border-border">
        <Button 
          className="w-full h-14 text-base font-semibold rounded-2xl shadow-lifted"
          onClick={generateInvoice}
          disabled={isGenerating}
        >
          {isGenerating ? (
            <>
              <Loader2 className="w-5 h-5 mr-2 animate-spin" />
              Generating...
            </>
          ) : (
            "Generate Invoice"
          )}
        </Button>
      </div>
    </div>
  );
};
